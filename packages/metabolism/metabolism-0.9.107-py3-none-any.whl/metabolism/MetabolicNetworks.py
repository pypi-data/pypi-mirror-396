from metabolism.CorrelationAnalyzer import CorrelationAnalyzer
from metabolism.Helper import Helper
import numpy as np
import pandas as pd
from scipy.stats import norm
import SimpleITK as sitk
from scipy.stats import gaussian_kde
import os,time
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

class Network:
    def __init__(self):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'
        self.correlationAnalyzer = CorrelationAnalyzer()
        self.helper = Helper()
    def process(self,dataset1,dataset2,modelname):
        pass
class GroupLevelNetwork(Network):
    def process_pcorr_diffgroup(self,dataset1,dataset2,modelname):
        pcorr1,df1 = self.dataset2pcorr(dataset1,modelname)
        pcorr2,df2 = self.dataset2pcorr(dataset2,modelname)
        numerator = pcorr1 - pcorr2
        denominator = pcorr1 + pcorr2
        denominator[denominator == 0] = 1e-6
        diffgroup = numerator / denominator
        print(f"[{self.SUCCESS_ICON}] group-level metabolic network DIFF is returned !!")
        return diffgroup
    def dataset2pcorr(self,dataset,modelname):
        df = self.correlationAnalyzer.dataset2df(dataset,modelname)
        print(f"[{self.INFO_ICON}] dataset:",dataset)
        print(f"[{self.SUCCESS_ICON}] dataset count:{len(df)}")
        pcorr = self.correlationAnalyzer.compute_partial_correlation_matrix(df,z=['Age', 'Sex', 'Weight'])
        return pcorr,df
    def dataset2pearson(self,dataset,modelname):
        df = self.correlationAnalyzer.dataset2df(dataset,modelname)
        df_ = df.drop(columns = ["Age","Sex","Weight"])
        print(f"[{self.INFO_ICON}] dataset:",dataset)
        print(f"[{self.SUCCESS_ICON}] dataset count:{len(df)}")
        corr,roi_name = self.correlationAnalyzer.compute_correlation_matrix(df_)
        return corr,roi_name

class IndividualNetwork(Network):
    def __init__(self,control,dataset2,modelname):
        super().__init__()
        print("="*20,"This method need one suv to create network !!")
        self.dataset1 = control
        self.dataset2 = dataset2
        self.modelname = modelname
    def process(self,referencenumber,covariate=['Age', 'Sex', 'Weight']):
        dataset1 = self.dataset1
        dataset2 = self.dataset2
        modelname = self.modelname
        df1 = self.correlationAnalyzer.dataset2df(dataset1,modelname)
        df2 = self.correlationAnalyzer.dataset2df(dataset2,modelname)
        self.df1 = df1
        self.df2 = df2
        print(f"[{self.INFO_ICON}] dataset1:",dataset1)
        print(f"[{self.SUCCESS_ICON}] dataset1 count:{len(df1)}")
        print(f"[{self.INFO_ICON}] dataset2:",dataset2)
        print(f"[{self.SUCCESS_ICON}] dataset2 count:{len(df2)}")
        df1_referece,df1_control = self.helper.split_dataframe(df1,referencenumber,random_seed=42)
        refnet = self.correlationAnalyzer.compute_partial_correlation_matrix(df1_referece,z=['Age', 'Sex', 'Weight'])

        edge_significant_counts = np.zeros_like(refnet, dtype=int)
        df2_zscores = []
        for i, row_dict in df2.iterrows():
            df1_referece_ = df1_referece.copy()
            current_row = pd.DataFrame([row_dict])
            combined = pd.concat([df1_referece_, current_row], ignore_index=True)
            # Perturbed network
            pnet = self.correlationAnalyzer.compute_partial_correlation_matrix(combined,z=['Age', 'Sex', 'Weight'])
            delta_pnet = pnet - refnet
            se = (1 - refnet**2) / (referencenumber - len(covariate) - 1)
            z_scores = delta_pnet / se
            df2_zscores.append(z_scores)

            p_values = 2 * norm.sf(np.abs(z_scores))
            num_edges = p_values.size - np.isnan(p_values).sum()
            alpha_corrected = 0.05 / num_edges
            significant_edges = p_values < alpha_corrected
            edge_significant_counts[significant_edges] += 1

        control_zscores = []
        for i, row_dict in df1_control.iterrows():
            df1_referece_ = df1_referece.copy()
            current_row = pd.DataFrame([row_dict])
            combined = pd.concat([df1_referece_, current_row], ignore_index=True)
            # Perturbed network
            pnet = self.correlationAnalyzer.compute_partial_correlation_matrix(combined,z=['Age', 'Sex', 'Weight'])
            delta_pnet = pnet - refnet
            se = (1 - refnet**2) / (referencenumber - len(covariate) - 1)
            z_scores = delta_pnet / se
            control_zscores.append(z_scores)
        self.control_zscores = control_zscores
        self.df2_zscores = df2_zscores
        self.edge_significant_counts = edge_significant_counts
        print(f"[{self.SUCCESS_ICON}SUCCESS] return dataset: control_zscores,df2_zscores,edge_significant_counts")
        return control_zscores,df2_zscores,edge_significant_counts
    def analyze_multiorgan(self):
        print(f"[{self.INFO_ICON}] multiorgan analyze starting")
        edge_significant_counts = self.edge_significant_counts
        df2_zscores = self.df2_zscores
        control_zscores = self.control_zscores
        
        mask_lower = np.triu(np.ones_like(edge_significant_counts, dtype=bool), k=1)
        edge_significant_counts[mask_lower] = 0
        rows, cols = np.where(edge_significant_counts != 0)
        values = self.edge_significant_counts[rows, cols]
        edges = list(zip(values, rows, cols))
        sorted_edges = sorted(edges, key=lambda x: x[0], reverse=True)

        columns = [x for x in self.df1.columns if x not in ['Age', 'Sex', 'Weight']]
        control_zscore_mean = np.mean(control_zscores,axis=0)
        df2_zscore_mean = np.mean(df2_zscores,axis=0)
        control_zscore_std = np.std(control_zscores,axis=0)
        df2_zscore_std = np.std(df2_zscores,axis=0)
        data_list = []
        
        for count,row,col in sorted_edges:
            if count < len(self.df2) * 0.2:
                continue
            roi1 = columns[row]
            roi2 = columns[col]
            meanz1 = df2_zscore_mean[row,col]
            stdz1 = df2_zscore_std[row,col]
            meanz2 = control_zscore_mean[row,col]
            stdz2 = control_zscore_std[row,col]
            data_list.append({"SignificantCount":count,"roi1":roi1,"roi2":roi2,"patient_z_mean":meanz1,
                 "patient_z_std":stdz1,"control_z_mean":meanz2,"control_z_std":stdz2})
        df = pd.DataFrame(data_list)
        print(f"[{self.SUCCESS_ICON}SUCCESS] return dataframe: SignificantCount,roi1,roi2,patient_z_mean,patient_z_std,control_z_mean,control_z_std")
        return df

    def analyze_singleorgan(self):
        print(f"[{self.INFO_ICON}] singleorgan analyze starting...")
        df2_zscores = self.df2_zscores
        control_zscores = self.control_zscores
        control_zscores = np.abs(np.array(control_zscores))
        df2_zscores = np.abs(np.array(df2_zscores))
        
        columns = [x for x in self.df1.columns if x not in ['Age', 'Sex', 'Weight']]
        data_list = []
        for i in range(len(columns)):
            roi = columns[i]
            control_degree = np.sum(control_zscores[:,i],axis=1)
            df2_degree = np.sum(df2_zscores[:,i],axis=1)
            df2_degree_max = np.max(df2_degree)
            df2_degree_mean = np.mean(df2_degree)
            df2_degree_std = np.std(df2_degree)
            control_degree_max = np.max(control_degree)
            control_degree_mean = np.mean(control_degree)
            control_degree_std = np.std(control_degree)
            data_list.append({"roi":roi,"patient_degree_max":df2_degree_max,"patient_degree_mean":df2_degree_mean,"patient_degree_std":df2_degree_std,
                              "control_degree_max":control_degree_max,"control_degree_mean":control_degree_mean,"control_degree_std":control_degree_std})
        df = pd.DataFrame(data_list)
        df = df.sort_values(by="patient_degree_mean", ascending=False)
        print(f"[{self.SUCCESS_ICON}SUCCESS] return dataframe: roi,patient_degree_max,patient_degree_mean,control_degree_max,control_degree_mean")
        return df

class KLNetwork(Network):
    def __init__(self,dataset,modelname):
        super().__init__()
        print("="*20,"\nThis method need one suv to create network !!\n","="*20)
        self.dataset = dataset
        self.modelname = modelname
    def process(self):
        dataset = self.dataset
        modelname = self.modelname
        print(f"[{self.INFO_ICON}] dataset:",dataset)
        for file in os.listdir(dataset):
            if "SUV" not in file or ".nii.gz" not in file:
                continue
            suv = os.path.join(dataset,file)
            segpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),"merge.nii.gz")
            npzpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),"KLSE_matrix.npz")
            print(suv)
            print(segpath)
            if not os.path.exists(segpath):
                print(f"[{self.ERROR_ICON}] No segment result for Model {modelname}\n    SUV path:{suv}")
                continue
            if os.path.exists(npzpath):
                print(f" [{self.SUCCESS_ICON} SKIP] Result has saved to:",npzpath)
                continue
            suv = sitk.ReadImage(suv)
            seg = sitk.ReadImage(segpath)
            # step1: get flatten value from each roi
            roi_intensities,roi_names = self.extract_roi_intensities(suv,seg)
            # step2: compute klse martix
            print(f" [{self.RUNNING_ICON}] Using KDE to estimate KLNetwork ...")
            # klse = self.compute_klse_matrix(roi_intensities)
            klse = self.compute_klse_matrix_parallel(roi_intensities)
            
            
            print(f" [{self.SUCCESS_ICON}] Estimation Success !! categoriy:{len(roi_names)}")
            roi_names = np.array(roi_names, dtype=object)
            np.savez_compressed(npzpath, 
                               klse_matrix=klse, 
                               roi_names=roi_names)
            print(f" [{self.SUCCESS_ICON}] Result saved to:",npzpath)

    def extract_roi_intensities(self,suv, seg):
        modelname = self.modelname
        seg = sitk.GetArrayFromImage(seg)
        suv = sitk.GetArrayFromImage(suv)
        if modelname == "mpum":
            atlasinfo = self.helper.get_mpum_categories()
            brainzone = [x for x in range(132,215)]
        roi_intensities = []
        roi_names = []
        for label in brainzone:
            mask = (seg == label)
            intensities = suv[mask].flatten()
            if label == 0:
                continue
            if len(intensities) == 0:
                continue
            roi_names.append(atlasinfo[str(label)])
            roi_intensities.append(intensities)
        return roi_intensities,roi_names
    def compute_klse_matrix(self,roi_intensities):
        """计算对称KL散度并生成KLSE矩阵"""
        epsilon=1e-8
        n_roi = len(roi_intensities)
        klse_matrix = np.zeros((n_roi, n_roi))
        
        # 为每个ROI构建KDE模型
        kdes = [gaussian_kde(roi) for roi in roi_intensities]
        
        for i in tqdm(range(n_roi)):
            for j in range(i, n_roi):
                if i == j:
                    klse_matrix[i,j] = 1.0  # 对角线元素为自连接
                    continue
                    
                # 获取KDE概率密度函数
                kde_p = kdes[i]
                kde_q = kdes[j]
                
                # 定义积分域（覆盖两个分布的联合范围）
                x_min = min(kde_p.dataset.min(), kde_q.dataset.min())
                x_max = max(kde_p.dataset.max(), kde_q.dataset.max())
                x = np.linspace(x_min, x_max, 1000)
                
                # 计算概率密度（防止零值）
                p = np.clip(kde_p(x), epsilon, None)
                q = np.clip(kde_q(x), epsilon, None)
                
                # 计算对称KL散度
                kl_pq = np.trapz(p * np.log(p/q), x)
                kl_qp = np.trapz(q * np.log(q/p), x)
                sym_kl = kl_pq + kl_qp
                
                # 计算KLSE连接强度
                klse = np.exp(-sym_kl)
                klse_matrix[i,j] = klse
                klse_matrix[j,i] = klse  # 对称赋值
        return klse_matrix

    def compute_klse_matrix_parallel(self, roi_intensities):
        n_roi = len(roi_intensities)
        klse_matrix = np.zeros((n_roi, n_roi))
        kdes = []
        for roi in roi_intensities:
            if len(roi) < 2:
                roi = np.repeat(roi, 2) + np.random.normal(0, 1e-6, size=2)
            kdes.append(gaussian_kde(roi))
        self.kdes = kdes
        # 预计算所有KDE的范围 [优化点1]
        self.mins = [kde.dataset.min() for kde in kdes]
        self.maxs = [kde.dataset.max() for kde in kdes]
        
        # 生成所有需要计算的(i,j)对 [优化点2]
        pairs = [(i, j) for i in range(n_roi) for j in range(i, n_roi)]
        # 启动多进程池
        with ProcessPoolExecutor(max_workers=int(16)) as executor:
            results = list(tqdm(executor.map(self._compute_pair, pairs), total=len(pairs)))
        
        # 填充矩阵
        for (i, j), val in results:
            klse_matrix[i, j] = klse_matrix[j, i] = val
        
        return klse_matrix
    def _compute_pair(self,pair):
        i, j = pair
        mins = self.mins
        maxs = self.maxs
        kdes = self.kdes
        if i == j:
            return (i, j), 1.0
        # 计算积分域
        x_min = min(mins[i], mins[j])
        x_max = max(maxs[i], maxs[j])
        x = np.linspace(x_min, x_max, 100)  # 减少采样点 [优化点3]
        # 向量化评估KDE [优化点4]
        p = np.clip(kdes[i](x), 1e-8, None)
        q = np.clip(kdes[j](x), 1e-8, None)
        # 快速积分计算
        sym_kl = np.trapz(p * np.log(p/q), x) + np.trapz(q * np.log(q/p), x)
        return (i, j), np.exp(-sym_kl)
    
    def analyze(self):
        dataset = self.dataset
        modelname = self.modelname
        print(f"[{self.INFO_ICON}] dataset:",dataset)

        all_roi_names = []
        valid_files = []

        for file in os.listdir(dataset):
            if "SUV" not in file or ".nii.gz" not in file:
                continue
            npzpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),"KLSE_matrix.npz")
            if not os.path.exists(npzpath):
                continue
            data = np.load(npzpath, allow_pickle=True)
            roi_names = data["roi_names"].tolist()
            all_roi_names.append(roi_names)
            valid_files.append(npzpath)

        if not valid_files:
            print(f"[{self.ERROR_ICON}] No valid KLSE files. Run .process() or check dataset path !!")
            return None,None
        else:
            print(f"[{self.INFO_ICON}] Find {len(valid_files)} KLSE data !!")

        common_roi = []
        if all_roi_names:
            base_names = all_roi_names[0]
            common_roi = [
                name for name in base_names 
                if all(name in names for names in all_roi_names[1:])
            ]
        print(f"[{self.SUCCESS_ICON}] Effective Region Count: {len(common_roi)}")
        
        processed_klses = []
        removed_records = []
        
        for file_idx, npz_path in enumerate(valid_files):
            data = np.load(npz_path, allow_pickle=True)
            original_klse = data["klse_matrix"]
            original_names = data["roi_names"].tolist()
            
            name_to_idx = {name: idx for idx, name in enumerate(original_names)}
            
            try:
                keep_indices = [name_to_idx[name] for name in common_roi]
            except KeyError as e:
                print(f" [{self.ERROR_ICON}] 文件 {npz_path} 缺失关键脑区: {e}")
                continue
            
            row_indices = np.array(keep_indices)[:, np.newaxis]
            col_indices = np.array(keep_indices)
            
            processed_klse = original_klse[row_indices, col_indices]
            
            removed = [name for name in original_names if name not in common_roi]
            if removed:
                print(f" [{self.SUCCESS_ICON}]  Remove region: {', '.join(removed)} from {npz_path}")
                removed_records.append((os.path.basename(npz_path), removed))
            
            processed_klses.append(processed_klse)
        
        if len(common_roi) == 0:
            print(f" [{self.ERROR_ICON}] No Common region ?!")
            return None, None
        
        self.klses = processed_klses
        self.common_roi_names = common_roi
        return processed_klses, common_roi