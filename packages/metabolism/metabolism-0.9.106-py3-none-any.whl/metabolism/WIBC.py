import SimpleITK as sitk
import numpy as np
import os,json
from pathlib import Path
import pandas as pd
from scipy import stats, linalg

class CorrelationAnalyzer:
    def __init__(self):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'
        pass
    def dataset2df(self,dataset,modelname):
        feats = []
        for file in os.listdir(dataset):
            if "SUV" not in file or ".nii.gz" not in file:
                continue
            suv = os.path.join(dataset,file)
            segpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),"merge.nii.gz")
            if not os.path.exists(segpath):
                print(f"[{self.ERROR_ICON}] No segment result for Model {modelname}\n    SUV path:{suv}")
                continue
            featpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),f"{modelname}#suvr.json")
            with open(featpath,"r") as f:
                feat = json.load(f)
            feats.append(feat)
        df = self._preprocess_feature(feats)
        return df
    def _preprocess_feature(self,feats):
        processed = []
        for feat in feats:
            try:
                subject_data = {
                    'Age': int(feat['age']),  # 转换字符串年龄为整数
                    'Sex': 0 if feat['gender'] == 'M' else 1,  # 性别编码
                    'Weight': feat['weight']
                }
                for key in feat:
                    if key in ['background', 'gender', 'age', 'weight','L-Substantia nigra','R-Substantia nigra']:
                        continue  #
                    subject_data[key] = feat[key]['meansuvr']
                processed.append(subject_data)
            except:
                pass
        return pd.DataFrame(processed)
    def compute_correlation_matrix(self,df):
        corr_matrix = df.corr(method='pearson')
        return corr_matrix.values,corr_matrix.columns.values
    def compute_partial_correlation_matrix(self,df,z=['Age', 'Sex', 'Weight']):
        '''partial correlation matrix: parital correlation between X and Y after removing linear effects of Z'''
        regions = [col for col in df.columns if col not in z]
        X = df[regions].values
        cover = []
        for zz in z:
            cover.append(df[zz].values)
        cover.append(np.ones(len(df)))
        covar = np.column_stack(cover)
        
        covar = (covar - covar.mean(axis=0)) / (covar.std(axis=0) + 1e-8)
        residuals = []
        for i in range(X.shape[1]):
            try:
                beta = linalg.lstsq(covar, X[:,i], cond=1e-6)[0]
            except:
                beta = np.dot(np.linalg.pinv(covar), X[:,i])
            resid = X[:,i] - np.dot(covar, beta)
            residuals.append(resid)
        
        residuals = np.array(residuals).T
        residuals += np.random.normal(0, 1e-8, residuals.shape)
        pcorr = np.corrcoef(residuals, rowvar=False)
        np.fill_diagonal(pcorr, 0)
        return pcorr