import torch
from .get_gpu import b_get_idle_gpu



def b_get_device(use_idle_gpu=False, sout=False):
    """
    获取最佳可用计算设备。

    设备选择优先级如下：
        1. NPU（如果安装了 torch_npu）
        2. GPU（若 use_idle_gpu=True 则选空闲 GPU，否则默认使用 "cuda"）
        3. CPU（兜底）

    参数
    ----------
    use_idle_gpu : bool, 可选
        是否自动选择最空闲的 GPU。
        - True  ：调用 b_get_idle_gpu() 选择负载最低的 GPU。
        - False ：直接使用默认 GPU（cuda:0）。
        默认值为 False。

    sout : bool, 可选
        是否打印设备选择的详细信息。
        打印示例：
            可用设备:['npu', 'cuda', 'cpu'], 使用npu
        默认值为 False。

    返回
    ----------
    torch.device
        根据优先级返回可用的设备对象：
        NPU → GPU → CPU。

    """
    lst = []
    # 优先使用NPU
    try:
        import torch_npu
        lst.append(torch.device("npu"))
    except ImportError:
        pass

    # 其次使用GPU
    if torch.cuda.is_available():
        if use_idle_gpu:
            lst.append(b_get_idle_gpu())
        else:
            lst.append(torch.device("cuda"))

    # 最后使用CPU
    lst.append(torch.device("cpu"))

    lst_str = [str(i) for i in lst]
    if sout:
        print(f"可用设备:{lst_str}, 使用{lst_str[0]}")
    return lst[0]


if __name__ == '__main__':
    result = b_get_device()
    print(result)
