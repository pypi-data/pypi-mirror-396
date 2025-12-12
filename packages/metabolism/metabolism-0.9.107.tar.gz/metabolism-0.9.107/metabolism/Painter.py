import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from metabolism.Helper import Helper
import seaborn as sns
import colorsys
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
from matplotlib import cm
import SimpleITK as sitk

class Painter:
    def __init__(self):
        self.helper = Helper()
        pass
    def hotmap_zscore(self,matrix):
        plt.figure(figsize=(4,4))
        mask = np.triu(np.ones_like(matrix,dtype=bool))
        sns.heatmap(
            matrix,
            annot=False,          # 在格子中显示数值
            fmt=".2f",           # 数值格式（保留两位小数）
            mask=mask,
            cmap='coolwarm',     # 颜色映射
            vmin=-3, vmax=3,     # 颜色范围
            square=True,         # 保持格子为正方形
            linewidths=0.5,      # 格子间线宽
            cbar=True,
            cbar_kws={'label': 'Correlation'}
        )
        plt.tight_layout()
        plt.show()
    def hotmap_zscore2(self,matrix1,matrix2,matrixtype):
        '''
            - matrixtype: "z-score" or "kldivergence"
        '''
        mask_lower = np.triu(np.ones_like(matrix1, dtype=bool), k=1)  # 隐藏上三角（含对角线）
        mask_upper = np.tril(np.ones_like(matrix2, dtype=bool), k=-1)  # 隐藏下三角（含对角线）
        fig, ax = plt.subplots(figsize=(5,4))
        if matrixtype == "z-score":
            vmin,vmax = -3,3
        elif matrixtype == "kldivergence":
            vmin,vmax = 0,1
        else:
            vmin,vmax = None,None
            print(f"matrixtype is wrong ! z-score or kldivergence !! ")
            # return None
        sns.heatmap(
            matrix1,
            mask=mask_lower,          # 隐藏上三角和对角线
            cmap='coolwarm',             # 下三角用蓝色系
            vmin=vmin, vmax=vmax,     # 颜色范围
            annot=False,
            fmt=".2f",
            square=True,
            linewidths=0.5,
            cbar=True,
            ax=ax
        )
        
        sns.heatmap(
            matrix2,
            mask=mask_upper,          # 隐藏下三角和对角线
            cmap='coolwarm',              # 上三角用红色系
            vmin=vmin, vmax=vmax,     # 颜色范围
            annot=False,
            fmt=".2f",
            square=True,
            linewidths=0.5,
            cbar=False,
            ax=ax
        )
        ax.plot(
            [matrix1.shape[0] + 1, 0],
            [matrix1.shape[0] + 1, 0],          # x从i到i+1
            color='red',         # 红色
            linewidth=2,         # 线宽
            transform=ax.transData,  # 使用数据坐标系
            clip_on=False,         # 避免边缘裁剪
            alpha=0.5
        )
        
        plt.tight_layout()
        plt.show()

    def show_slices(self,suv_volume, roi_volume, x=None, y=None, z=None):
        suv_volume = self.helper.resample_to_isotropic(suv_volume, new_spacing=[2.0, 2.0, 2.0],interpolator=sitk.sitkLinear)
        roi_volume = self.helper.resample_to_isotropic(roi_volume, new_spacing=[2.0, 2.0, 2.0],interpolator=sitk.sitkNearestNeighbor)
        suv_volume = sitk.GetArrayFromImage(suv_volume)
        roi_volume = sitk.GetArrayFromImage(roi_volume)
        
        roi_labels = np.unique(roi_volume)
        roi_labels = roi_labels[roi_labels != 0]
        
        colors = cm.get_cmap('tab20', len(roi_labels))
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        slices = [
            ("Axial",   roi_volume[x, :, :] if x is not None else roi_volume.shape[0]//2, x),
            ("Coronal", roi_volume[:, y, :] if y is not None else roi_volume.shape[1]//2, y),
            ("Sagittal",roi_volume[:, :, z] if z is not None else roi_volume.shape[2]//2, z)
        ]
        
        for ax, (title, slc, pos) in zip(axes, slices):
            suv_slice = suv_volume[pos, :, :] if title == "Axial" else \
                        suv_volume[:, pos, :] if title == "Coronal" else \
                        suv_volume[:, :, pos]
            ax.imshow(suv_slice.T, cmap="gray", origin="lower")
            
            for i, label in enumerate(roi_labels):
                mask = (slc == label).T
                color = colors(i)
                ax.contour(mask, colors=[color], linewidths=1.2, levels=[0.5])
                
            ax.set_title(f"{title} View\nPosition: {pos}")
            ax.axis("off")
    
        legend_elements = [plt.Line2D([0], [0], color=colors(i), lw=2, label=f'ROI {label}') 
                          for i, label in enumerate(roi_labels)]
        
        plt.tight_layout()
        plt.show()
    def hotmap_edge(self,matrix):
        plt.figure(figsize=(4,4))
        mask = np.triu(np.ones_like(matrix,dtype=bool))
        vmax = np.max(matrix)  # 获取数据最大值
        sns.heatmap(
            matrix,
            annot=False,          # 在格子中显示数值
            fmt=".2f",           # 数值格式（保留两位小数）
            mask=mask,
            cmap='coolwarm',     # 颜色映射
            square=True,         # 保持格子为正方形
            linewidths=0.5,      # 格子间线宽
            cbar=True,
            cbar_kws={'label': 'Correlation'}
        )
        plt.tight_layout()
        plt.show()