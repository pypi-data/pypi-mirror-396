
"""
wimc.py — Whole-body Individual Metabolic Connectomics (WIMC)
-------------------------------------------------------------
Utilities to parse PET/CT + segmentation subjects, extract SUV features,
build a CONTROL reference model (ROI selection, covariate regression,
pairwise linear relations), and compute patient-specific studentized
error matrices (individual metabolic networks).

Author: ChatGPT (GPT-5 Thinking)
Date: 2025-08-11

Quick usage
-----------
# 1) Build control model from a control dataset
from wimc import WIMC

w = WIMC(dataset_root="/share/home/yxchen/dataset/qianfoshan/healthy_nifti_process/")
# Process all control subjects (cached if suv_roi_feature.json exists)
control_results = w.run(show_progress=True)

# Build control reference (choose coverage threshold and references)
control_model, control_train = w.build_control_reference(
    coverage_threshold=0.80,
    brain_ref=['Brainstem'],
    body_ref='liver'   # <-- ensure this matches your ROI column name (case-insensitive supported)
)

# 2) Compute patient networks from a separate patient dataset root
sr_mats, patient_resid, patient_subjects = w.process_patients_from_root(
    patients_root="/path/to/patient_root",
    use_cache=True
)

# sr_mats: numpy array (S, N, N) studentized error matrices per patient
# patient_resid: residual DataFrame (covariates removed using CONTROL formulas)
# patient_subjects: list of subject folder names in the same order as sr_mats
#
# You can interpret larger sr values as stronger deviations from CONTROL pairwise relations.

Notes
-----
- The WIMC instance should be created using the *CONTROL* dataset root.
- When patient data arrives, you can process it via process_patients_from_root(), which will:
    (1) fill/clean using CONTROL-chosen ROIs and CONTROL means,
    (2) compute relative SUVs using CONTROL references,
    (3) regress out age/sex using CONTROL-fitted formulas,
    (4) compute studentized error matrices using CONTROL pairwise model.
"""

import os
import re
import glob
import json
from typing import Optional, List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import SimpleITK as sitk
from tqdm import tqdm
from itertools import combinations
from sklearn.linear_model import LinearRegression

# ----------------------------
# Helpers
# ----------------------------

def _largest_by_size(paths: List[str]) -> Optional[str]:
    if not paths:
        return None
    return max(paths, key=lambda p: os.path.getsize(p))

def _rmse(y, yhat) -> float:
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    if y.size == 0:
        return np.nan
    return float(np.sqrt(np.mean((y - yhat) ** 2)))

def _to_scalar(o):
    import numpy as _np
    if isinstance(o, _np.generic):
        return o.item()
    return o

# ----------------------------
# Main class
# ----------------------------

class WIMC:
    def __init__(
        self,
        dataset_root: str,
        atlasinfo_path: Optional[str] = None,
        output_root: Optional[str] = None,
        label_range: Tuple[int, int] = (3, 215),
        hist_bins: Optional[np.ndarray] = None,
        pet_patterns: Optional[List[str]] = None,
        ct_keyword: str = "CT",
        seg_filename_candidates: Optional[List[str]] = None,
    ):
        """
        Create a WIMC instance bound to a CONTROL dataset root.

        Parameters
        ----------
        dataset_root : str
            Root directory where each sub-folder is a subject with PET/CT NIfTI and segmentation.
        atlasinfo_path : Optional[str]
            Optional global readme.json mapping label indices -> ROI names.
        output_root : Optional[str]
            Where to store cached per-subject suv_roi_feature.json; default: subject folder itself.
        label_range : (int, int)
            Inclusive-exclusive ROI label index range (default [3, 215)).
        hist_bins : np.ndarray
            Bins for SUV histograms (default: 0..30 step 0.1 plus +inf bucket).
        pet_patterns : list[str]
            Glob patterns to find PET (SUV) images (default tries several common variants).
        ct_keyword : str
            Substring to identify CT file among *.nii.gz in a subject folder (default 'CT').
        seg_filename_candidates : list[str]
            Patterns for segmentation filename(s), 'merge.nii.gz' prioritized.
        """
        self.dataset_root = os.path.abspath(dataset_root)
        if not os.path.isdir(self.dataset_root):
            raise NotADirectoryError(f"dataset_root not found: {self.dataset_root}")

        self.output_root = output_root
        self.label_start, self.label_stop = label_range

        # Histogram bins default
        if hist_bins is None:
            bins = np.arange(0, 30.1, 0.1)
            self.hist_bins = np.append(bins, np.inf)
        else:
            self.hist_bins = hist_bins

        # PET filename patterns
        self.pet_patterns = pet_patterns or [
            "SUVTBW*.nii.gz", "TBWSUV*.nii.gz", "*SUV*TBW*.nii.gz", "*SUV*.nii.gz", "*PT*.nii.gz"
        ]

        # Segmentation filename patterns
        self.seg_filename_candidates = seg_filename_candidates or [
            "merge.nii.gz", "*merge*.nii.gz", "*seg*.nii.gz"
        ]

        self.ct_keyword = ct_keyword

        # atlasinfo mapping
        self.global_atlasinfo = None
        if atlasinfo_path is not None and os.path.isfile(atlasinfo_path):
            with open(atlasinfo_path, "r") as f:
                self.global_atlasinfo = json.load(f)

        self.results_per_subject: List[Dict[str, Any]] = []  # raw per-subject json-able results

        # CONTROL model store
        self.control_model: Dict[str, Any] = {}

    # ---------- IO helpers ----------
    @staticmethod
    def _read_image(path: str) -> sitk.Image:
        return sitk.ReadImage(path)

    @staticmethod
    def _resample_to_reference(image: sitk.Image, reference: sitk.Image, interpolator: int, default: float = 0.0) -> sitk.Image:
        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(reference)
        resampler.SetInterpolator(interpolator)
        resampler.SetOutputSpacing(reference.GetSpacing())
        resampler.SetOutputOrigin(reference.GetOrigin())
        resampler.SetOutputDirection(reference.GetDirection())
        resampler.SetSize(reference.GetSize())
        resampler.SetDefaultPixelValue(default)
        return resampler.Execute(image)

    def _find_ct(self, subject_dir: str) -> Optional[str]:
        cands = [os.path.join(subject_dir, f) for f in os.listdir(subject_dir)
                 if f.endswith(".nii.gz") and self.ct_keyword in f]
        return _largest_by_size(cands)

    def _find_pet(self, subject_dir: str) -> Optional[str]:
        cands = []
        for pat in self.pet_patterns:
            cands.extend(glob.glob(os.path.join(subject_dir, pat)))
        cands = sorted(set(cands))
        return _largest_by_size(cands)

    def _find_seg(self, subject_dir: str, ct_path: Optional[str]) -> Optional[str]:
        # 1) direct candidates in subject_dir
        for pat in self.seg_filename_candidates:
            hits = glob.glob(os.path.join(subject_dir, pat))
            if hits:
                return _largest_by_size(hits)
        # 2) mpum#<ctbase>/merge.nii.gz style
        if ct_path is not None:
            ct_base = os.path.basename(ct_path).replace(".nii.gz", "")
            sub = f"mpum#{ct_base}"
            mpum_dir = os.path.join(subject_dir, sub)
            for pat in self.seg_filename_candidates:
                hits = glob.glob(os.path.join(mpum_dir, pat))
                if hits:
                    return _largest_by_size(hits)
        # 3) recursive fallback
        for pat in self.seg_filename_candidates:
            hits = glob.glob(os.path.join(subject_dir, "**", pat), recursive=True)
            if hits:
                return _largest_by_size(hits)
        return None

    def _find_info_csv(self, subject_dir: str) -> Optional[str]:
        p = os.path.join(subject_dir, "info.csv")
        return p if os.path.isfile(p) else None

    def _find_readme_json(self, subject_dir: str) -> Optional[str]:
        p = os.path.join(subject_dir, "readme.json")
        if os.path.isfile(p):
            return p
        hits = glob.glob(os.path.join(subject_dir, "**", "readme.json"), recursive=True)
        return hits[0] if hits else None

    # ---------- Subject cache ----------
    def _get_subject_cache_path(self, subject_name: str) -> str:
        if self.output_root:
            out_dir = os.path.join(self.output_root, subject_name)
        else:
            out_dir = os.path.join(self.dataset_root, subject_name)
        os.makedirs(out_dir, exist_ok=True)
        return os.path.join(out_dir, "suv_roi_feature.json")

    def _save_subject_result(self, subject_name: str, result: Dict[str, Any]) -> None:
        out_path = self._get_subject_cache_path(subject_name)
        with open(out_path, "w") as f:
            json.dump(result, f, default=_to_scalar)

    # ---------- ROI feature extraction ----------
    def _extract_roi_features(self, pet_img: sitk.Image, seg_img: sitk.Image, atlasinfo: Optional[Dict[str, str]]) -> Dict[str, Any]:
        pet = sitk.GetArrayFromImage(pet_img)
        seg = sitk.GetArrayFromImage(seg_img)
        out: Dict[str, Any] = {}
        for i in range(self.label_start, self.label_stop):
            mask = (seg == i)
            count = int(mask.sum())
            if count == 0:
                continue
            vals = pet[mask]
            mean_suv = float(np.mean(vals))
            max_suv = float(np.max(vals))
            hist, _ = np.histogram(vals, bins=self.hist_bins)
            roi_name = None
            if atlasinfo is not None and str(i) in atlasinfo:
                roi_name = atlasinfo[str(i)]
            elif atlasinfo is not None and i in atlasinfo:
                roi_name = atlasinfo[i]
            else:
                roi_name = f"label_{i}"
            out[roi_name] = {
                "label_index": int(i),
                "voxel_count": count,
                "meansuv": mean_suv,
                "maxsuv": max_suv,
                "hist": [int(h) for h in hist]
            }
        return out

    # ---------- Subject processing (with cache) ----------
    def process_subject(self, subject_dir: str, force: bool = False) -> Optional[Dict[str, Any]]:
        subject_dir = os.path.abspath(subject_dir)
        subject_name = os.path.basename(subject_dir)

        # 1) Cache
        cache_path = self._get_subject_cache_path(subject_name)
        if (not force) and os.path.isfile(cache_path):
            try:
                with open(cache_path, "r") as f:
                    cached = json.load(f)
                cached.setdefault("subject", subject_name)
                return cached
            except Exception:
                pass  # fallthrough to recompute

        # 2) Locate files
        ct_path  = self._find_ct(subject_dir)
        pet_path = self._find_pet(subject_dir)
        seg_path = self._find_seg(subject_dir, ct_path)
        info_csv = self._find_info_csv(subject_dir)
        readme_json = self._find_readme_json(subject_dir)

        if not (ct_path and pet_path and seg_path):
            return None

        # 3) Read & resample
        ct_img  = self._read_image(ct_path)
        pet_img = self._read_image(pet_path)
        seg_img = self._read_image(seg_path)

        pet_r = self._resample_to_reference(pet_img, ct_img, sitk.sitkLinear, default=0.0)
        seg_r = self._resample_to_reference(seg_img, ct_img, sitk.sitkNearestNeighbor, default=0)

        # 4) atlasinfo
        atlasinfo = None
        if readme_json and os.path.isfile(readme_json):
            with open(readme_json, "r") as f:
                atlasinfo = json.load(f)
        elif self.global_atlasinfo is not None:
            atlasinfo = self.global_atlasinfo

        roi_features = self._extract_roi_features(pet_r, seg_r, atlasinfo)

        # demographics
        demo: Dict[str, Any] = {}
        if info_csv and os.path.isfile(info_csv):
            try:
                df = pd.read_csv(info_csv)
                if "Gender" in df.columns:
                    demo["sex"] = str(df["Gender"].values[0])
                if "Age" in df.columns:
                    try:
                        demo["age"] = float(df["Age"].values[0])
                    except Exception:
                        demo["age"] = None
            except Exception:
                pass

        result = {
            "subject": subject_name,
            "paths": {"ct": ct_path, "pet": pet_path, "seg": seg_path},
            **demo,
            "roi_features": roi_features
        }
        self._save_subject_result(subject_name, result)
        return result

    # ---------- Batch processing ----------
    def run(self, show_progress: bool = True) -> List[Dict[str, Any]]:
        subjects = [os.path.join(self.dataset_root, d) for d in os.listdir(self.dataset_root)
                    if os.path.isdir(os.path.join(self.dataset_root, d))]
        it = tqdm(subjects, desc="WIMC") if show_progress else subjects
        results = []
        for sd in it:
            r = self.process_subject(sd, force=False)
            if r is not None:
                results.append(r)
        self.results_per_subject = results
        return results

    # ---------- Flatten to DataFrame ----------
    def to_dataframe(self, results: Optional[List[Dict[str, Any]]] = None) -> pd.DataFrame:
        results = results if results is not None else self.results_per_subject
        rows = []
        for r in results:
            subj = r.get("subject")
            sex  = r.get("sex", None)
            age  = r.get("age", None)
            rf   = r.get("roi_features", {})
            for roi_name, feat in rf.items():
                rows.append({
                    "subject": subj,
                    "sex": 1 if str(sex).upper().startswith("M") else 0 if sex is not None else np.nan,
                    "age": age,
                    "roi": roi_name,
                    "label_index": feat.get("label_index"),
                    "voxel_count": feat.get("voxel_count"),
                    "meansuv": feat.get("meansuv"),
                    "maxsuv": feat.get("maxsuv"),
                    "hist": feat.get("hist"),
                })
        return pd.DataFrame(rows)

    # ---------- Dict structure adapters ----------
    @staticmethod
    def _region_map(subj: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(subj, dict) and "roi_features" in subj:
            return subj["roi_features"]
        # flattened fallback
        return {k: v for k, v in subj.items() if isinstance(v, dict) and "meansuv" in v}

    @staticmethod
    def _get_age_sex(subj: Dict[str, Any]):
        return subj.get("age", None), subj.get("sex", None)

    # ---------- Fill/Clean/Select ----------
    def fill_and_clean(
        self,
        source_data: List[Dict[str, Any]],
        target_data: List[Dict[str, Any]],
        coverage_threshold: float = 0.80,
        regions: Optional[List[str]] = None,
        fill_target_only: bool = True
    ):
        from collections import Counter
        import copy

        # Regions by coverage
        if regions is None:
            cnt = Counter()
            for subj in source_data:
                rmap = self._region_map(subj)
                cnt.update(rmap.keys())
            n = max(len(source_data), 1)
            REGIONS = [k for k, c in cnt.items() if c / n >= coverage_threshold]
            REGIONS_REMOVE = [k for k, c in cnt.items() if c / n < coverage_threshold]
        else:
            REGIONS = list(regions)
            REGIONS_REMOVE = []

        # Compute region means in source (used to fill)
        region_means = {}
        for r in REGIONS:
            vals = []
            for subj in source_data:
                rmap = self._region_map(subj)
                if r in rmap and "meansuv" in rmap[r]:
                    vals.append(rmap[r]["meansuv"])
            region_means[r] = float(np.mean(vals)) if len(vals) > 0 else 0.0

        def _filled_copy(dataset, do_fill: bool):
            out = []
            for subj in dataset:
                subj_cp = json.loads(json.dumps(subj))  # deep copy (JSON-safe)
                rmap = self._region_map(subj_cp)
                if do_fill:
                    for r in REGIONS:
                        if r not in rmap:
                            rmap[r] = {"meansuv": region_means[r]}
                        elif "meansuv" not in rmap[r]:
                            rmap[r]["meansuv"] = region_means[r]
                # write back
                if "roi_features" in subj_cp:
                    subj_cp["roi_features"] = rmap
                else:
                    for r, v in rmap.items():
                        subj_cp[r] = v
                out.append(subj_cp)
            return out

        train_filled = _filled_copy(source_data, do_fill=not fill_target_only)
        target_filled = _filled_copy(target_data, do_fill=True)

        def _has_all_regions(subj):
            rmap = self._region_map(subj)
            for r in REGIONS:
                if r not in rmap or "meansuv" not in rmap[r]:
                    return False
            return True

        train_clean = [s for s in train_filled if _has_all_regions(s)]
        target_clean = [s for s in target_filled if _has_all_regions(s)]

        def _to_df(stage):
            rows = []
            for s in stage:
                age, sex = self._get_age_sex(s)
                rmap = self._region_map(s)
                row = {
                    "age": np.nan if age is None else float(age),
                    "sex": 1 if str(sex).upper().startswith("M") else 0 if sex is not None else np.nan
                }
                for r in REGIONS:
                    row[r] = rmap[r]["meansuv"]
                rows.append(row)
            return pd.DataFrame(rows)

        train_df = _to_df(train_clean)
        target_df = _to_df(target_clean)

        return REGIONS, REGIONS_REMOVE, region_means, train_df, target_df

    # ---------- Relative SUV ----------
    def compute_relative_suv(self, data_df: pd.DataFrame, REGIONS: List[str], brain_ref: List[str], body_ref: str) -> pd.DataFrame:
        """Return DataFrame with ['age','sex', *<roi>_rel] using given references.
        Case-insensitive matching for reference column names is supported.
        """
        # Case-insensitive lookup for references
        colmap_lower = {c.lower(): c for c in data_df.columns}
        # brain_ref columns
        brain_ref_cols = []
        for br in brain_ref:
            key = br.lower()
            if key not in colmap_lower:
                raise KeyError(f"brain_ref '{br}' not found among columns: {list(data_df.columns)[:10]}... (total {len(data_df.columns)})")
            brain_ref_cols.append(colmap_lower[key])
        # body_ref column
        body_ref_col = colmap_lower.get(body_ref.lower(), None)
        if body_ref_col is None:
            raise KeyError(f"body_ref '{body_ref}' not found among columns: {list(data_df.columns)[:10]}... (total {len(data_df.columns)})")

        # Heuristics: brain vs body regions
        brain_regions = [r for r in REGIONS if any(x in r for x in ['L-', 'R-', 'Third ventricle', 'Corpus callosum'])]
        body_regions  = [r for r in REGIONS if r not in brain_regions and r not in brain_ref_cols and r != body_ref_col]

        eps = 1e-8
        denom_brain = data_df[brain_ref_cols].mean(axis=1).replace(0, eps)
        denom_body  = data_df[body_ref_col].replace(0, eps)

        brain_rel = data_df[brain_regions].div(denom_brain, axis=0)
        brain_rel.columns = [f"{c}_rel" for c in brain_rel.columns]

        body_rel = data_df[body_regions].div(denom_body, axis=0)
        body_rel.columns = [f"{c}_rel" for c in body_rel.columns]

        return pd.concat([data_df[['age', 'sex']], brain_rel, body_rel], axis=1)

    # ---------- Covariate regression (CONTROL fit) ----------
    def fit_covariate_models(self, rel_df: pd.DataFrame, covariates: Optional[List[str]] = None):
        covariates = covariates or ["age", "sex"]
        feat_cols = [c for c in rel_df.columns if c.endswith("_rel")]
        X = rel_df[covariates].values.astype(float)

        coefs = np.zeros((len(feat_cols), len(covariates)), dtype=float)
        intrc = np.zeros((len(feat_cols),), dtype=float)

        for idx, col in enumerate(feat_cols):
            y = rel_df[col].values.astype(float)
            mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
            if mask.sum() >= 3:
                mdl = LinearRegression().fit(X[mask], y[mask])
                coefs[idx, :] = mdl.coef_.ravel()
                intrc[idx] = float(mdl.intercept_)
            else:
                coefs[idx, :] = 0.0
                intrc[idx] = 0.0

        model = {
            "covariates": covariates,
            "feature_cols": feat_cols,
            "coef": coefs,   # shape (p, q)
            "intercept": intrc  # shape (p,)
        }
        return model

    def apply_covariate_models(self, rel_df: pd.DataFrame, cov_model: Dict[str, Any]) -> pd.DataFrame:
        covariates = cov_model["covariates"]
        feat_cols  = cov_model["feature_cols"]
        coefs      = cov_model["coef"]
        intrc      = cov_model["intercept"]

        X = rel_df[covariates].values.astype(float)
        resid = {}
        for i, col in enumerate(feat_cols):
            y = rel_df[col].values.astype(float)
            yhat = intrc[i] + X @ coefs[i, :].reshape(-1, 1)
            yhat = yhat.ravel()
            rr = y - yhat
            resid[col] = rr
        resid_df = pd.DataFrame(resid, index=rel_df.index)
        return resid_df

    # ---------- Pairwise linear (CONTROL fit) ----------
    def fit_pairwise_linear(self, resid_df: pd.DataFrame):
        feat_cols = [c for c in resid_df.columns if c.endswith("_rel")]
        F = len(feat_cols)
        slope_mat  = np.zeros((F, F), dtype=float)
        interc_mat = np.zeros((F, F), dtype=float)
        rmse_mat   = np.zeros((F, F), dtype=float)
        r2_mat     = np.zeros((F, F), dtype=float)
        np.fill_diagonal(r2_mat, 1.0)

        for i, j in combinations(range(F), 2):
            yi = resid_df[feat_cols[i]].values
            xj = resid_df[feat_cols[j]].values.reshape(-1, 1)
            mask = np.isfinite(yi) & np.isfinite(xj).ravel()
            if mask.sum() >= 3:
                mdl = LinearRegression().fit(xj[mask], yi[mask])
                yhat = mdl.predict(xj[mask])
                slope_mat[i, j]  = float(mdl.coef_[0])
                interc_mat[i, j] = float(mdl.intercept_)
                rmse_mat[i, j]   = _rmse(yi[mask], yhat)
                r2_mat[i, j]     = float(mdl.score(xj[mask], yi[mask]))
            else:
                slope_mat[i, j]  = np.nan
                interc_mat[i, j] = np.nan
                rmse_mat[i, j]   = np.nan
                r2_mat[i, j]     = np.nan

            # reverse direction
            yj = resid_df[feat_cols[j]].values
            xi = resid_df[feat_cols[i]].values.reshape(-1, 1)
            mask = np.isfinite(yj) & np.isfinite(xi).ravel()
            if mask.sum() >= 3:
                mdl = LinearRegression().fit(xi[mask], yj[mask])
                yhat = mdl.predict(xi[mask])
                slope_mat[j, i]  = float(mdl.coef_[0])
                interc_mat[j, i] = float(mdl.intercept_)
                rmse_mat[j, i]   = _rmse(yj[mask], yhat)
                r2_mat[j, i]     = float(mdl.score(xi[mask], yj[mask]))
            else:
                slope_mat[j, i]  = np.nan
                interc_mat[j, i] = np.nan
                rmse_mat[j, i]   = np.nan
                r2_mat[j, i]     = np.nan

        return {
            "feature_cols": feat_cols,  # order of *_rel features
            "slope": slope_mat,
            "intercept": interc_mat,
            "sigma": rmse_mat,
            "r2": r2_mat
        }

    # ---------- CONTROL reference pipeline ----------
    def build_control_reference(
        self,
        coverage_threshold: float = 0.80,
        brain_ref: Optional[List[str]] = None,
        body_ref: str = "liver",
        regions: Optional[List[str]] = None
    ):
        """
        Build and cache the CONTROL model:
          - ROI selection by coverage
          - Region means for filling
          - Relative SUV (given references)
          - Covariate regressions (age, sex)
          - Pairwise linear relationships

        Returns
        -------
        control_model : dict
        control_train_resid : pd.DataFrame
        """
        brain_ref = brain_ref or ["Brainstem"]

        if not self.results_per_subject:
            # if run() hasn't been called, process control root now
            self.run(show_progress=True)

        # Select/Fill/Clean using CONTROL itself
        REGIONS, REGIONS_REMOVE, region_means, train_df, _ = self.fill_and_clean(
            source_data=self.results_per_subject,
            target_data=[],
            coverage_threshold=coverage_threshold,
            regions=regions,
            fill_target_only=False
        )

        # Relative SUVs
        train_rel = self.compute_relative_suv(train_df, REGIONS, brain_ref=brain_ref, body_ref=body_ref)

        # Covariate models (fit on CONTROL)
        cov_model = self.fit_covariate_models(train_rel, covariates=["age", "sex"])

        # Residuals for CONTROL
        control_resid = self.apply_covariate_models(train_rel, cov_model)

        # Pairwise relations (fit on CONTROL residuals)
        pair_model = self.fit_pairwise_linear(control_resid)

        # Persist control model pieces
        self.control_model = {
            "REGIONS": REGIONS,
            "REGIONS_REMOVE": REGIONS_REMOVE,
            "region_means": region_means,
            "brain_ref": brain_ref,
            "body_ref": body_ref,
            "cov_model": cov_model,
            "pair_model": pair_model
        }
        return self.control_model, control_resid

    # ---------- Studentized matrices for a dataset ----------
    def studentized_matrices(self, resid_df: pd.DataFrame, pair_model: Dict[str, Any]) -> np.ndarray:
        """Compute per-sample studentized error matrices using CONTROL pairwise params.

        sr_ij = | y_i - (b0_ij + b1_ij * x_j) | / sigma_ij
        where y_i is residual of feature i, x_j is residual of feature j.
        """
        feat_cols = pair_model["feature_cols"]
        slope = pair_model["slope"]
        interc = pair_model["intercept"]
        sigma = pair_model["sigma"]

        # Ensure columns order matches
        X = resid_df[feat_cols].values  # shape: (S, N)
        S, N = X.shape
        out = np.zeros((S, N, N), dtype=float)

        for s in range(S):
            xs = X[s, :]  # residuals vector length N
            for i, j in combinations(range(N), 2):
                if not np.isfinite(slope[i, j]) or not np.isfinite(interc[i, j]) or not np.isfinite(sigma[i, j]) or sigma[i, j] == 0:
                    sr = np.nan
                else:
                    y_i = xs[i]
                    x_j = xs[j]
                    yhat = interc[i, j] + slope[i, j] * x_j
                    sr = abs(y_i - yhat) / (sigma[i, j] if sigma[i, j] != 0 else 1e-8)
                out[s, i, j] = out[s, j, i] = sr
            # diagonal remains 0
        return out

    # ---------- Patient pipeline ----------
    def process_patients_from_root(self, patients_root: str, use_cache: bool = True):
        """
        Process a patient dataset root using the CONTROL model previously built.

        Returns
        -------
        sr_mats : np.ndarray, shape (S, N, N)
            Studentized error matrices per patient (individual networks).
        patient_resid : pd.DataFrame
            Residual features per patient after removing covariates using CONTROL formulas.
        patient_subjects : List[str]
            Subject folder names in order of sr_mats rows.
        """
        if not self.control_model:
            raise RuntimeError("CONTROL model is empty. Call build_control_reference() first.")

        # 1) Collect patients results
        patients_root = os.path.abspath(patients_root)
        if not os.path.isdir(patients_root):
            raise NotADirectoryError(f"patients_root not found: {patients_root}")
        subj_dirs = [os.path.join(patients_root, d) for d in os.listdir(patients_root)
                     if os.path.isdir(os.path.join(patients_root, d))]

        results_patient = []
        subjects = []
        it = tqdm(subj_dirs, desc="WIMC-PATIENT")
        for sd in it:
            r = self.process_subject(sd, force=not use_cache)
            if r is not None:
                results_patient.append(r)
                subjects.append(os.path.basename(sd))

        # 2) Fill/Clean using CONTROL-chosen REGIONS and CONTROL means
        REGIONS = self.control_model["REGIONS"]
        region_means = self.control_model["region_means"]

        # assemble filled DataFrame
        def subj_to_row(subj):
            rmap = self._region_map(subj)
            age, sex = self._get_age_sex(subj)
            row = {
                "age": np.nan if age is None else float(age),
                "sex": 1 if str(sex).upper().startswith("M") else 0 if sex is not None else np.nan
            }
            ok = True
            for r in REGIONS:
                if r in rmap and "meansuv" in rmap[r]:
                    row[r] = rmap[r]["meansuv"]
                else:
                    # fill from CONTROL mean
                    row[r] = region_means.get(r, 0.0)
            return row

        patient_df = pd.DataFrame([subj_to_row(s) for s in results_patient])

        # 3) Relative SUVs with CONTROL refs
        brain_ref = self.control_model["brain_ref"]
        body_ref  = self.control_model["body_ref"]
        patient_rel = self.compute_relative_suv(patient_df, REGIONS, brain_ref=brain_ref, body_ref=body_ref)

        # 4) Remove covariates using CONTROL formulas
        cov_model = self.control_model["cov_model"]
        patient_resid = self.apply_covariate_models(patient_rel, cov_model)

        # 5) Studentized matrices using CONTROL pairwise model
        pair_model = self.control_model["pair_model"]
        sr_mats = self.studentized_matrices(patient_resid, pair_model)

        return sr_mats, patient_resid, subjects
