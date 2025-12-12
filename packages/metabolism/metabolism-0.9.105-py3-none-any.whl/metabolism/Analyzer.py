import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.stats import mannwhitneyu
from scipy.stats import ks_2samp
from scipy.stats import brunnermunzel
from scipy.stats import permutation_test
from scipy.stats import ttest_ind

from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
from sklearn.cluster import KMeans
from scipy.sparse.csgraph import laplacian
import networkx as nx
from networkx.algorithms.community import modularity
from metabolism.CorrelationAnalyzer import CorrelationAnalyzer
from metabolism.Helper import Helper

class SingleAnalyzer:
    def __init__(self,control,patient,modelname,suvrelative="brain"):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'
        self.control = control
        self.patient = patient
        self.modelname = modelname
        self.suvrelative = suvrelative
        self.correlationAnalyzer = CorrelationAnalyzer()
        self.helper = Helper()
    def process_group2one(self):
        control = self.control
        patient = self.patient
        modelname = self.modelname
        df1 = self.correlationAnalyzer.dataset2df(control,modelname)
        df2 = self.correlationAnalyzer.dataset2df(patient,modelname)
        self.control_suv = df1
        self.patient_suv = df2
        print(f"[{self.INFO_ICON}] control:",control,f"count:{len(df1)}")
        print(f"[{self.INFO_ICON}] patient:",patient,f"count:{len(df2)}")
        brainzone = df1.columns.values
        brainzone = [b for b in brainzone if b not in ["Age","Sex","Weight"]]
        if self.suvrelative == "brain":
            row_means = df1[brainzone].mean(axis=1)
        if self.suvrelative == "brainstem":
            row_means = df1[["Brainstem"]].mean(axis=1)
        df1[brainzone] = df1[brainzone].div(row_means, axis=0)
        if self.suvrelative == "brain":
            row_means = df2[brainzone].mean(axis=1)
        if self.suvrelative == "brainstem":
            row_means = df2[["Brainstem"]].mean(axis=1)
        df2[brainzone] = df2[brainzone].div(row_means, axis=0)
        self.control_suvr = df1
        self.patient_suvr = df2
        control_result = {}
        for key in df1.columns:
            if key in ["Age","Sex","Weight"]:
                continue
            if self.suvrelative == "brainstem":
                if key == 'Brainstem':
                    continue
            d1 = df1[key].values
            mu, sigma = np.mean(d1), np.std(d1)
            ks_stat, ks_p = stats.kstest(d1, 'norm', args=(mu, sigma))
            if ks_p < 0.05:
                print(f"{key}不服从正态分布")
            d1 = df1[key].values
            df_avg = np.mean(d1)
            df_min = np.mean(d1)
            control_result[key] = {"mean":np.mean(d1),"std":np.std(d1),"min":np.min(d1),"max":np.max(d1)}
        patient_result = []
        for idx in range(len(df2)):
            tmp = df2.iloc[idx]
            oneresult = {}
            for key in control_result:
                d2 = tmp[key]
                oneresult[key] = (d2 - control_result[key]["mean"]) / control_result[key]["std"]
            patient_result.append(oneresult)
        return control_result, patient_result

class PairAnalyzer:
    def __init__(self):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'

    def intersubject_dissimilarity(self,matrixs,roi_names):
        print(f"[{self.INFO_ICON}] Dissimilarity -1 to 1.")
        matrixs = np.array(matrixs)
        dissimilarity_mean = np.zeros_like(roi_names)
        dissimilarity_std = np.zeros_like(roi_names)
        for i,roi_name in enumerate(roi_names):
            corr = np.corrcoef(matrixs[:,i])
            dissimilarity_mean[i] = np.mean(-corr)
            dissimilarity_std[i] = np.std(-corr)
        df = pd.DataFrame({"roi":roi_names,"dissimilarity_mean":dissimilarity_mean,"dissimilarity_std":dissimilarity_std})
        print(f"[{self.SUCCESS_ICON}] df columns: roi, dissimilarity_mean, dissimilarity_std")
        return df

    def roipair_compare_group4group(self,matrixs1,matrixs2,roi_names,pmethod="mannwhitneyu"):
        print(f"[{self.INFO_ICON}] If roi-roi pair has significant difference between two groups.")
        if len(matrixs2) <=1:
            print(f"[{self.ERROR_ICON}] matrixs2 has one data, Please use function 'roipair_compare_group4one' !! ")
            return None
        matrixs1 = np.array(matrixs1)
        matrixs2 = np.array(matrixs2)
        results = []
        for i in range(len(roi_names)):
            for j in range(i+1,len(roi_names)):
                data1 = matrixs1[:,i,j]
                data2 = matrixs2[:,i,j]
                if pmethod == "mannwhitneyu":
                    stat, p = mannwhitneyu(data1, data2, alternative='two-sided')
                elif pmethod == "kolmogoerov_smirnov":
                    stat, p = ks_2samp(data1, data2)
                elif pmethod == "brunnermunzel":
                    stat, p = brunnermunzel(data1, data2)
                elif pmethod == "t":
                    stat, p = ttest_ind(data1,data2, equal_var=False)
                row = {
                    'roi1': roi_names[i],
                    'roi2': roi_names[j],
                    'group1':np.mean(data1),
                    'group2':np.mean(data2),
                    'p': p,
                }
                results.append(row)
        df = pd.DataFrame(results)
        total_comparisons = len(df)  # ROI对的总数
        corrected_alpha = 0.05 / total_comparisons
        df['significant'] = df['p'] < corrected_alpha
        return df

    def roipair_compare_group4one(self,matrixs1,matrixs2,roi_names):
        print(f"[{self.INFO_ICON}] When matrix2 is a single data, you can calculate its distance from the mean of matrixs1 ")
        matrixs1 = np.array(matrixs1)
        matrixs2 = np.array(matrixs2)
        results = []
        for i in range(len(roi_names)):
            for j in range(i+1,len(roi_names)):
                data1 = matrixs1[:,i,j]
                data2 = matrixs2[0,i,j]
                row = {
                    'roi1': roi_names[i],
                    'roi2': roi_names[j],
                    'group1_mean':np.mean(data1),
                    'group1_std':np.std(data1),
                    'data2':data2,
                    'z-score':(data2-np.mean(data1)) / np.std(data1)
                }
                results.append(row)
        df = pd.DataFrame(results)
        df = df.sort_values(
            by="z-score",
            key=lambda x: x.abs(),  
            ascending=False        
        )
        return df

    def roi_compare_group4one(self,matrixs1,matrixs2,roi_names):
        print(f"[{self.INFO_ICON}] When matrix2 is a single data, you can calculate its distance from the mean of matrixs1 ")
        matrixs1 = np.array(matrixs1)
        matrixs2 = np.array(matrixs2)
        results = []
        for i in range(len(roi_names)):
            data1 = np.mean(matrixs1[:,i],axis=0)
            data2 = np.mean(matrixs2[0,i])
            row = {
                'roi': roi_names[i],
                'group1_mean':np.mean(data1),
                'group1_std':np.std(data1),
                'data2':data2,
                'z-score':(data2-np.mean(data1)) / np.std(data1)
            }
            results.append(row)
        df = pd.DataFrame(results)
        df = df.sort_values(
            by="z-score",
            key=lambda x: x.abs(),  
            ascending=False        
        )
        return df
        
class GraphAnalyzer:
    def __init__(self):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'

    def feature_extract_from_matrix(self,matrix,roi_name):
        degree =self.node_degree(matrix)
        clustering_coeff = self.weighted_clustering_coeff(matrix)
        centrality = self.eigenvector_centrality(matrix)
        self.spectral_clustering(matrix)
        mask_lower = np.triu(np.ones_like(matrix, dtype=bool), k=1)
        feat = matrix[mask_lower].flatten()
        feat_name = np.array([f"{roi_name[i]}_{roi_name[j]}" for i in range(0,len(roi_name)) for j in range(i+1,len(roi_name))])
        feat = np.concatenate([feat,degree, clustering_coeff,centrality])
        feat_name = np.concatenate([feat_name,
                                    [f"{roi}_degree" for roi in roi_name],
                                    [f"{roi}_clustering" for roi in roi_name],
                                    [f"{roi}_centrality" for roi in roi_name]])
        return feat,feat_name
    def node_degree(self,matrix):
        print(f"[{self.RUNNING_ICON}] node degree (节点度) ...")
        degree = np.sum(matrix,axis=0)
        print(f"[{self.SUCCESS_ICON}] node degree (节点度) ...")
        return degree
    def spectral_clustering(self,matrix):
        print(f"[{self.RUNNING_ICON}] spectral clustering (谱聚类) ...")
        L = laplacian(matrix, normed=True) 
        eigenvaLlues, eigenvectors = np.linalg.eigh(L)
        k = 3  # 预设社区数量
        best_Q = -1
        best_k = -1
        for k in range(3,15):
            top_k_vectors = eigenvectors[:, :k]  
            kmeans = KMeans(n_clusters=k).fit(top_k_vectors)
            labels = kmeans.labels_ 
            G = nx.from_numpy_array(matrix)
            communities = []
            for cluster_id in np.unique(labels):
                nodes = np.where(labels == cluster_id)[0].tolist()
                communities.append(set(nodes)) 
            Q = modularity(G, communities)
            if best_Q < Q:
                best_Q = Q
                best_k = k
        if best_Q < 0.3:
            print(f"[{self.ERROR_ICON}] 不存在显著社区 ")
        else:
            print(f"[{self.SUCCESS_ICON}] 存在显著社区 Best K: {best_k} || Best Q: {round(best_Q,2)} ")
    
    def weighted_clustering_coeff(self,matrix):
        print(f"[{self.RUNNING_ICON}] weighted clustering coeff (加权聚类系数) ...")
        """
        处理连续权重无向图的聚类系数
        :param matrix: 对称矩阵，对角线为0
        :return: 各节点的加权聚类系数（0~1）
        """
        n = matrix.shape[0]
        np.fill_diagonal(matrix, 0)  # 确保无自环
        W = np.copy(matrix)
        
        # 计算二值化度数
        binary_adj = (W > 0).astype(int)
        degrees = np.sum(binary_adj, axis=1)
        
        coeffs = np.zeros(n)
        for i in range(n):
            if degrees[i] < 2:
                continue
                
            # 获取邻居索引
            neighbors = np.where(binary_adj[i] > 0)[0]
            
            # 计算所有邻居对的三元乘积
            triple_sum = 0.0
            for j in range(len(neighbors)):
                for k in range(j+1, len(neighbors)):
                    n1, n2 = neighbors[j], neighbors[k]
                    triple_prod = W[i,n1] * W[i,n2] * W[n1,n2]
                    triple_sum += np.cbrt(triple_prod)  # 立方根处理
                    
            coeffs[i] = 2 * triple_sum / (degrees[i] * (degrees[i]-1))
        print(f"[{self.SUCCESS_ICON}] weighted clustering coeff (加权聚类系数) ...")
        return coeffs

    def eigenvector_centrality(self,matrix):
        print(f"[{self.RUNNING_ICON}] centrality (特征向量中心性) ...")
        """
        处理连续权重矩阵的特征向量中心性
        :param matrix: 对称权重矩阵
        :return: 归一化的特征向量中心性
        """
        # 对称性检查
        if not np.allclose(matrix, matrix.T):
            matrix = (matrix + matrix.T) / 2
        vals, vecs = eigsh(matrix, k=1, which='LM')
        centrality = np.abs(vecs[:,0])
        print(f"[{self.SUCCESS_ICON}] centrality (特征向量中心性) ...")
        return (centrality - centrality.min()) / (centrality.max() - centrality.min())