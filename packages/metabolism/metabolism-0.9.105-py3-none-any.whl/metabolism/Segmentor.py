import sys,os
import requests
from tqdm import tqdm
from metabolism.MPUM.inference import inference as MPUM_inference
from pathlib import Path
LIB_ROOT = Path(__file__).parent
class Segmentor:
    def __init__(self):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'
        
        report = check_pytorch_environment()
        print_diagnostics(report)
        if report["message"] == "GPU is available":
            print(f"[{self.SUCCESS_ICON}Diagnosis] GPU is available !!")
        elif report["message"] == "Only CPU":
            print(f"[{self.SUCCESS_ICON}Diagnosis] CPU is OK but GPU would be much more faster !!")
        else:
            print(f"[{self.ERROR_ICON}Diagnosis] Please check PyTorch is installed correctly !!")
    def load_model(self,modelname="mpum"):
        os.makedirs(f"{LIB_ROOT}/weights",exist_ok=True)
        if modelname == "mpum":
            print(f"[{self.INFO_ICON}Model] You select MPUM !")
            print(f"[{self.INFO_ICON}Model] Checking Model weights !")
            download = False
            if not os.path.exists(f"{LIB_ROOT}/weights/fold0.pth"):
                download = True
            if not os.path.exists(f"{LIB_ROOT}/weights/fold1.pth"):
                download = True
            if not os.path.exists(f"{LIB_ROOT}/weights/fold2.pth"):
                download = True
            if download:
                print(f" [{self.RUNNING_ICON}] Downloading Weights!")
                url = 'https://pku-milab-model.oss-ap-northeast-1.aliyuncs.com/fold0.pth'
                response = requests.get(url, stream=True)
                total_size_in_bytes = int(response.headers.get('content-length', 0))
                with open(f'{LIB_ROOT}/weights/fold0.pth', 'wb') as file:
                    with tqdm(total=total_size_in_bytes, unit='B', unit_scale=True) as bar:
                        for chunk in response.iter_content(chunk_size=1024):
                            file.write(chunk)
                            bar.update(len(chunk)) 
                url = 'https://pku-milab-model.oss-ap-northeast-1.aliyuncs.com/fold1.pth'
                response = requests.get(url, stream=True)
                total_size_in_bytes = int(response.headers.get('content-length', 0))
                with open(f'{LIB_ROOT}/weights/fold1.pth', 'wb') as file:
                    with tqdm(total=total_size_in_bytes, unit='B', unit_scale=True) as bar:
                        for chunk in response.iter_content(chunk_size=1024):
                            file.write(chunk)
                            bar.update(len(chunk))
                url = 'https://pku-milab-model.oss-ap-northeast-1.aliyuncs.com/fold2.pth'
                response = requests.get(url, stream=True)
                total_size_in_bytes = int(response.headers.get('content-length', 0))
                with open(f'{LIB_ROOT}/weights/fold2.pth', 'wb') as file:
                    with tqdm(total=total_size_in_bytes, unit='B', unit_scale=True) as bar:
                        for chunk in response.iter_content(chunk_size=1024):
                            file.write(chunk)
                            bar.update(len(chunk)) 
            print(f"[{self.SUCCESS_ICON}] Weights Finished!")

    
    def inference(self,modelname,input_nifti_path,modality,output_dir,targetpart="all"):
        if modelname == "mpum":
            check = True
            if not os.path.exists(f"{LIB_ROOT}/weights/fold0.pth"):
                download = False
            if not os.path.exists(f"{LIB_ROOT}/weights/fold1.pth"):
                download = False
            if not os.path.exists(f"{LIB_ROOT}/weights/fold2.pth"):
                download = False
            print(f"[{self.SUCCESS_ICON}] Model:{modelname}, Modality:{modality}, Model is ready !!")
            config = {
                    "tissue":targetpart,
                    "modality":modality,
                    "modelsize":"base",
                    "modalitydimension":512,
                    "ckpt":[f"{LIB_ROOT}/weights/fold0.pth",]
                             f"{LIB_ROOT}/weights/fold1.pth",
                             f"{LIB_ROOT}/weights/fold2.pth"]
                
            }
            MPUM_inference(config,
                     nii_path=input_nifti_path,
                     output_seg_path=output_dir)

    def inference_all(self,nifti_dataset,targetpart="all",modalities=["CT","SUV"]):
        print(f"\n{'='*30}\nProcessing NIFTI dataset: {nifti_dataset}")
        for case_name in os.listdir(nifti_dataset):
            print(f" [{self.INFO_ICON}Case] Processing: {case_name}")
            for nifti_name in os.listdir(os.path.join(nifti_dataset,case_name)):
                print(f"  [{self.INFO_ICON}NIFTI] Processing: {nifti_name}")
                if ".nii.gz" not in nifti_name:
                    continue
                ## First judgement
                modality = self.modality_judgement1(nifti_name)
                if modality == "UN":
                    print(f"   [{self.ERROR_ICON}Modality] Can not judge the modality of nifti !!")
                    continue
                if modality == 'CT' and modality in modalities:
                    self.inference(modelname='mpum',
                                   input_nifti_path=os.path.join(nifti_dataset,case_name,nifti_name),
                                   modality="ct",
                                   output_dir=os.path.join(nifti_dataset,case_name,"mpum#"+nifti_name.replace(".nii.gz","")),
                                   targetpart=targetpart)
                    # print(f"   [{self.INFO_ICON}Modality] Skip {modality}")
                if modality == "SUV" and modality in modalities:
                    self.inference(modelname='mpum',
                                   input_nifti_path=os.path.join(nifti_dataset,case_name,nifti_name),
                                   modality="pet",
                                   output_dir=os.path.join(nifti_dataset,case_name,"mpum#"+nifti_name.replace(".nii.gz","")),
                                   targetpart=targetpart)
                print(f"   [{self.SUCCESS_ICON}] Inference Success !!")
                
    def modality_judgement1(self,filename):
        if "ct#" in filename.lower() or 'ct_' in filename.lower():
            return "CT"
        if "suv" in filename.lower() or 'suv_' in filename.lower():
            return "SUV"
        if "pet#" in filename.lower() or 'pet_' in filename.lower():
            return "PET"
        if "DynamicPET" in filename:
            return "DynamicPET"
        return "UN"

def check_pytorch_environment():
    """检查PyTorch环境和GPU可用性"""
    env_info = {}

    try:
        import torch
        env_info['pytorch_installed'] = True
        env_info['pytorch_version'] = torch.__version__
    except ImportError:
        return {
            'status': 'missing',
            'message': "PyTorch need to be installed",
            'solution': "please run command: conda install pytorch torchvision cudatoolkit=11.3 -c pytorch\nOR pip install torch torchvision"
        }

    cuda_available = torch.cuda.is_available()
    env_info['cuda_available'] = cuda_available
    
    if cuda_available:
        env_info.update({
            'cuda_version': torch.version.cuda,
            'device_count': torch.cuda.device_count(),
            'current_device': torch.cuda.current_device(),
            'device_name': torch.cuda.get_device_name(),
            'device_capability': torch.cuda.get_device_capability(),
            'device_memory': f"{torch.cuda.get_device_properties(0).total_memory/1024**3:.2f} GB"
        })

        try:
            x = torch.randn(3, 3).cuda()
            y = torch.randn(3, 3).cuda()
            _ = torch.mm(x, y)  # 矩阵乘法测试
            
            with torch.cuda.device(0):
                torch.cuda.empty_cache()
                allocated = torch.cuda.memory_allocated()
                reserved = torch.cuda.memory_reserved()
                
            env_info['gpu_test_passed'] = True
            env_info['memory_status'] = {
                'allocated': f"{allocated/1024**2:.2f} MB",
                'reserved': f"{reserved/1024**2:.2f} MB"
            }

        except RuntimeError as e:
            return {
                'status': 'error',
                'message': f"GPU operation failed: {str(e)}",
                'diagnostics': env_info,
                'solution': "Please check the consistency of CUDA driver and PyTorch version"
            }

    return {
        'status': 'ok' if cuda_available else 'cpu_only',
        'message': "GPU is available" if cuda_available else "Only CPU",
        'diagnostics': env_info
    }

def print_diagnostics(report):
    """格式化输出诊断信息"""
    print("\n==== Pytorch and GPU Diagnosis ====")
    
    if report['status'] == 'missing':
        print(f"紧急: {report['message']}")
        print(f"解决方案: {report['solution']}")
        return

    print(f"PyTorch Version: {report['diagnostics']['pytorch_version']}")
    
    if report['diagnostics']['cuda_available']:
        print("\n[GPU 信息]")
        print(f"CUDA Version: {report['diagnostics']['cuda_version']}")
        print(f"Device Count: {report['diagnostics']['device_count']}")
        print(f"Device Name: {report['diagnostics']['device_name']}")
        print(f"Device Memory: {report['diagnostics']['device_memory']}")
    print("\n===================================")
    