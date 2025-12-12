from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (accuracy_score, classification_report, 
                             roc_auc_score, roc_curve, auc)
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
import matplotlib.pyplot as plt
import numpy as np

class Classifier:
    def __init__(self, model_name='xgboost',classnum=2, **model_params):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'
        self.model_name = model_name.lower()
        self.model = None
        self.classes_ = None
        self._init_model(classnum=classnum, **model_params)
        self.classnum = classnum

    def _init_model(self, classnum, **params):
        """初始化支持多分类的模型"""
        model_config = {
            'xgboost': {
                'class': XGBClassifier,
                'default': {
                    'n_estimators': 100,
                    'random_state': 42,
                    'objective': 'binary:logistic' if classnum == 2 else 'multi:softmax',
                }
            },
            'rf': {
                'class': RandomForestClassifier,
                'default': {
                    'n_estimators': 100,
                    'random_state': 42,
                    'class_weight': 'balanced'
                }
            },
            'svm': {
                'class': SVC,
                'default': {
                    'probability': True,
                    'random_state': 42,
                    'decision_function_shape': 'ovr' if classnum > 2 else 'ovo'
                }
            },
            'lr': {
                'class': LogisticRegression,
                'default': {
                    'max_iter': 1000,
                    'random_state': 42,
                    'multi_class': 'multinomial' if classnum > 2 else 'auto',
                    'solver': 'lbfgs' if classnum > 2 else 'liblinear'
                }
            },
            'knn': {
                'class': KNeighborsClassifier,
                'default': {
                    'n_neighbors': 5,
                    'weights': 'distance'
                }
            }
        }
        
        if self.model_name not in model_config:
            raise ValueError(f"{self.ERROR_ICON} 不支持模型类型，可选: {list(model_config.keys())}")
            
        config = model_config[self.model_name]
        final_params = {
            **config['default'],
            **{k: v for k, v in params.items() if k not in ['classnum']}
        }
        
        if classnum > 2 and self.model_name in ['svm', 'lr']:
            if 'OneVsRest' not in str(config['class']):
                self.model = OneVsRestClassifier(config['class'](**final_params))
        else:
            self.model = config['class'](**final_params)
            
        print(f"{self.SUCCESS_ICON} {self.model_name.upper()} 分类器初始化成功")

    def fit(self, X_train, y_train):
        """训练流程增强"""
        self.classes_ = np.unique(y_train)
        
        if len(self.classes_) != self.classnum:
            raise ValueError(
                f"{self.ERROR_ICON} 类别数不匹配！输入数据有{len(self.classes_)}类，但设置classnum={self.classnum}"
            )
        
        if self.model_name == 'xgboost':
            if self.classnum > 2 and 'num_class' not in self.model.get_params():
                self.model.set_params(num_class=self.classnum)
            elif self.classnum == 2 and self.model.objective.startswith('multi'):
                self.model.set_params(objective='binary:logistic')
            
        print(f"{self.RUNNING_ICON} 开始训练... (类别数: {len(self.classes_)})")
        self.model.fit(X_train, y_train)
        print(f"{self.SUCCESS_ICON} 训练完成")
        return self
    
    def predict(self, X_test):
        print(f"{self.RUNNING_ICON} 生成预测...")
        X_test = np.array(X_test)
        return self.model.predict(X_test)
    
    def predict_proba(self, X_test):
        """获取类别概率"""
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_test)
        raise ValueError(f"{self.ERROR_ICON} 该模型不支持概率预测")

    def evaluate(self, X_test, y_test):
        """多分类评估指标"""
        y_pred = self.predict(X_test)
        y_prob = self.predict_proba(X_test)
        
        # 基础指标
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        
        # ROC AUC计算
        if len(self.classes_) == 2:
            roc_auc = roc_auc_score(y_test, y_prob[:, 1])
        else:
            y_test_bin = label_binarize(y_test, classes=self.classes_)
            roc_auc = roc_auc_score(y_test_bin, y_prob, multi_class='ovr')
        
        print(f"\n{self.INFO_ICON} 分类报告:")
        print(report)
        print(f"{self.INFO_ICON} ROC AUC: {roc_auc:.4f}")
        return {'accuracy': acc, 'roc_auc': roc_auc}

    def plot_roc_curve(self, X_test, y_test,category_name,savepath=None):
        """绘制多类别ROC曲线"""
        y_prob = self.predict_proba(X_test)
        n_classes = len(self.classes_)
        
        # 二分类处理
        if n_classes == 2:
            fpr, tpr, _ = roc_curve(y_test, y_prob[:, 1])
            roc_auc = auc(fpr, tpr)
            
            plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.2f})')
        # 多分类处理
        else:
            y_test_bin = label_binarize(y_test, classes=self.classes_)
            fpr = dict()
            tpr = dict()
            roc_auc = dict()
            
            for i in range(n_classes):
                fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
                roc_auc[i] = auc(fpr[i], tpr[i])
            
            # 绘制每个类别的曲线
            for i in range(n_classes):
                plt.plot(fpr[i], tpr[i], 
                         label=f'{category_name[i]} (AUC = {roc_auc[i]:.2f})')
            
            # 计算宏平均
            all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))
            mean_tpr = np.zeros_like(all_fpr)
            for i in range(n_classes):
                mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])
            mean_tpr /= n_classes
            macro_auc = auc(all_fpr, mean_tpr)
            plt.plot(all_fpr, mean_tpr, 'k--', 
                     label=f'Macro-average (AUC = {macro_auc:.2f})')

        plt.plot([0, 1], [0, 1], 'r--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Multi-class ROC Curve')
        plt.legend(loc="lower right")
        if savepath is not None:
            plt.savefig(savepath,dpi=300,bbox_inches='tight')
        plt.show()