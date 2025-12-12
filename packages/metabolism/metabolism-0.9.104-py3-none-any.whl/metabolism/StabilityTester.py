from metabolism.Helper import Helper
from metabolism.CorrelationAnalyzer import CorrelationAnalyzer
import SimpleITK as sitk
import numpy as np
import os,json
from pathlib import Path
import pandas as pd
from scipy import stats, linalg

def resample_image(input_image, reference_image,default=0):
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(reference_image)
    
    resampler.SetInterpolator(sitk.sitkNearestNeighbor)
    
    resampler.SetOutputSpacing(reference_image.GetSpacing())
    resampler.SetOutputOrigin(reference_image.GetOrigin())
    resampler.SetOutputDirection(reference_image.GetDirection())
    
    resampler.SetSize(reference_image.GetSize())
    resampler.SetDefaultPixelValue(default)
    return resampler.Execute(input_image)


class StabilityTester:
    def __init__(self):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'
        print(f"[{self.INFO_ICON}] This class aims to find the number of reference group and control group for perturbed methods !!")

        self.correlationAnalyzer = CorrelationAnalyzer()
        self.helper = Helper()
    def suvseg2feature(self,dataset,modelname):
        print(f"[{self.INFO_ICON}] Load SUV and SEG from :", dataset)
        infos = pd.read_csv(os.path.join(dataset,"info.csv"))
        for file in os.listdir(dataset):
            if "SUV" not in file or ".nii.gz" not in file:
                continue
            print("-"*20)
            suv = os.path.join(dataset,file)
            segpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),"merge.nii.gz")
            if not os.path.exists(segpath):
                print(f"[{self.ERROR_ICON}] No segment result for Model {modelname}\n    SUV path:{suv}")
                continue
            print(f" [{self.RUNNING_ICON }] Processing: {suv}")
            suv = sitk.ReadImage(suv)
            seg = sitk.ReadImage(segpath)
            suv = resample_image(suv,seg,default=0)
            featpath = f"{Path(segpath).parent}/{modelname}#suvr.json"
            feat = self.extract_suv_based_roi(suv,seg,modelname=modelname)
            print("#".join(file.replace(".nii.gz","").split("#")[1:]))
            tmp = infos[infos.name == "#".join(file.replace(".nii.gz","").split("#")[1:])]
            gender = tmp.Gender.values[0]
            try: 
                age = float(tmp.Age.values[0])
            except:
                age = "Unknown"
            try:
                weight = float(tmp.Weight.values[0])
            except:
                age = "Unknown"
            feat.update({'gender':gender,"age":age,"weight":weight})
            with open(featpath,"w") as f:
                json.dump(feat,f)
            print(f" [{self.SUCCESS_ICON}SUCCESS] roi features are written into: {featpath}")
    def analyze(self,dataset,modelname):
        print(f"[{self.INFO_ICON}] Load FEAT from :", dataset)
        df = self.correlationAnalyzer.dataset2df(dataset,modelname)
        result = self.helper.detailed_nan_inspection(df)
        if result["msg"] == "error":
            print(f"[{self.ERROR_ICON} WRONG] Feature has NAN or INF")
        else:
            print(f"[{self.SUCCESS_ICON} SUCCESS] Feature has no NAN or INF")
        print('-'*20)
        print(f"[{self.INFO_ICON}] Starting stability Test. Data Count:{len(df)}")
        self.full_refnetwork = self.correlationAnalyzer.compute_partial_correlation_matrix(df)
        results = {}
        for n in range(10,len(df)+1):
            mean_,std_ = self.bootstrap_pcorr_stability(df,resample_size=n,n_iter=100)
            results[n] = (mean_,std_)
            print(f" [{self.SUCCESS_ICON}] resample size:{n}, correlation coefficient:{mean_}")
        return df,results
    
    def bootstrap_pcorr_stability(self,df, resample_size, n_iter=20, seed=42):
        np.random.seed(seed)
        covar_cols = ['Age', 'Sex', 'Weight']  # 根据实际情况修改
        all_pcorr_flatten = []
        correlations = []
        for _ in range(n_iter):
            idx = np.random.choice(df.index,size=resample_size,replace=False)
            sub_df = df.loc[idx].copy()
            sub_refnetwork = self.correlationAnalyzer.compute_partial_correlation_matrix(sub_df,z=['Age', 'Sex', 'Weight'])
            
            flat_full = self.full_refnetwork[~np.eye(self.full_refnetwork.shape[0], dtype=bool)]
            flat_sub = sub_refnetwork[~np.eye(sub_refnetwork.shape[0], dtype=bool)]
            r = np.corrcoef(flat_full, flat_sub)[0,1]
            correlations.append(r)
        return np.mean(correlations), np.std(correlations)
    
    def extract_suv_based_roi(self,suv,seg,modelname):
        seg = sitk.GetArrayFromImage(seg)
        suv = sitk.GetArrayFromImage(suv)
        if modelname == "mpum":
            atlasinfo = self.helper.get_mpum_categories()
            brainzone= [x for x in range(132,215)]
        op = {}
        mask = np.isin(seg, brainzone)
        meanAllBrainSUV = np.mean(suv[mask])
        for i in range(0,len(atlasinfo)):
            tmp = suv[seg == i]
            if len(tmp) == 0:
                continue
            meansuvr = np.mean(tmp) / meanAllBrainSUV
            maxsuvr = np.max(tmp) / meanAllBrainSUV
            op[atlasinfo[str(i)]] = {"meansuvr":float(meansuvr),"maxsuvr":float(maxsuvr)}
        return op