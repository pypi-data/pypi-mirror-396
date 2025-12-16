import torch
from torch import nn

from ..Btrainer import B_Trainer, B_Classification_Trainer
from ..Butils import b_get_device

class testNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer0 = nn.Sequential(
            nn.Linear(1*28*28, 64),
            nn.ReLU(),
            nn.Linear(64, 10)
        )
    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.layer0(x)
        return x

def get_dataset():
    from torch.utils.data import TensorDataset
    from torch.utils.data import random_split, DataLoader
    # 随机生成数据张量和标签张量
    data = torch.randn(6000, 1, 28, 28)
    labels = torch.randint(0, 10, (6000,)) # 标签为0~9, shape=(6000,)
    # 创建TensorDataset对象
    datasets = TensorDataset(data, labels)
    # 随机划分训练集和验证集
    train_datasets, val_datasets = random_split(datasets, [5500, 500])
    # 创建DataLoader对象
    return train_datasets, val_datasets

def b_test_trainer():
    print(f"{'='*10} test.py start {'='*10}")

    #### 超参数 ####
    lr = 1e-4
    batch_size = 64
    epochs = 5
    device = b_get_device(sout=True)

    #### 数据集 ####
    train_dataset, val_dataset = get_dataset()
    print(f"{'='*10} TensorDataset 创建完成 {'='*10}")

    #### 模型 ####
    net = testNet()
    net.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)
    #### Trainer ####
    myTrainer = B_Trainer(
        model=net,
        batch_size=batch_size,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        optimizer=optimizer,
        criterion=criterion,
        device=device,
        isDistributedDataParallel=True
    )
    #### 训练 ####
    myTrainer.train_eval_s(epochs)
    accuracy, inference_time, params, outputs_list, labels_list = myTrainer.calculate_model()
    print(f"accuracy: {accuracy}")
    print(f"inference_time: {inference_time}")
    print(f"params: {params}")

    print(f"{'='*10} test.py success {'='*10}")

def b_test_classfication_trainer():
    print(f"{'='*10} test.py start {'='*10}")

    #### 超参数 ####
    lr = 1e-4
    batch_size = 64
    epochs = 5
    device = b_get_device(sout=True)

    #### 数据集 ####
    train_dataset, val_dataset = get_dataset()
    print(f"{'='*10} TensorDataset 创建完成 {'='*10}")

    #### 模型 ####
    net = testNet()
    net.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)
    #### Trainer ####
    myTrainer = B_Classification_Trainer(
        model=net,
        batch_size=batch_size,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        optimizer=optimizer,
        criterion=criterion,
        device=device,
        isDistributedDataParallel=True
    )
    #### 训练 ####
    myTrainer.train_eval_s(epochs)
    accuracy, f1_score, confusion_matrix, inference_time, params = myTrainer.calculate_model()
    print(f"accuracy: {accuracy}")
    print(f"f1_score: {f1_score}")
    print(f"confusion_matrix: \n{confusion_matrix}")
    print(f"inference_time: {inference_time}")
    print(f"params: {params}")

    print(f"{'='*10} test.py success {'='*10}")

if __name__ == '__main__':
    b_test_trainer()