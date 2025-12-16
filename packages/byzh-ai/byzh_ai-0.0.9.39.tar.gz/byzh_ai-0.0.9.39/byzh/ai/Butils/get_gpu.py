import subprocess
import torch

def b_get_gpu_nvidia():
    """
    - GPU 索引（index）
    - GPU 名称（name）
    - GPU 利用率（utilization.gpu, %）
    - GPU 已使用显存（memory.used, MiB）
    - GPU 总显存（memory.total, MiB）

    Returns [[gpu_index, gpu_name, gpu_util, memory_used, memory_total], ...]
    """
    result = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
        encoding='utf-8'
    )
    gpus = []
    for line in result.strip().split('\n'):
        if line:
            gpu_index, gpu_name, memory_used, memory_total, gpu_util = line.split(', ')
            gpus.append([int(gpu_index), str(gpu_name), float(gpu_util), int(memory_used), int(memory_total)])
    return gpus

def b_get_idle_gpu():
    """
    得到更少被使用的cuda设备
    """
    gpus = b_get_gpu_nvidia()
    rates = [gpu[-2]/gpu[-1] for gpu in gpus]
    index = rates.index(min(rates))
    return torch.device(f"cuda:{index}")

if __name__ == '__main__':
    gpus = b_get_gpu_nvidia()
    for gpu in gpus:
        print(gpu)
        # [0, 'NVIDIA GeForce RTX 4090', 32.0, 3854, 24564]
        # [1, 'NVIDIA GeForce RTX 4090', 33.0, 891, 24564]

    print(b_get_idle_gpu())
