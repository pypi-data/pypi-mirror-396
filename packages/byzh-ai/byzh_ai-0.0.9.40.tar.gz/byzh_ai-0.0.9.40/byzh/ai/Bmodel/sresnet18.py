from torch import nn
from torch.nn import functional as F
import torch

from spikingjelly.activation_based import layer, neuron, functional, surrogate


'''
输入：[b,3,224,224]
-> [t,b,3,224,224]

-> [t,b,64,112,112] (conv)[1]
   [t,b,64,56,56] (maxpool)

-> [t,b,64,56,56] (conv)[2]
   [t,b,64,56,56] (conv)[3]
   [t,b,64,56,56] (conv)[4]
   [t,b,64,56,56] (conv)[5]

-> [t,b,128,28,28] (conv)[6]
   [t,b,128,28,28] (conv)[7]
   [t,b,128,28,28] (conv)[8]
   [t,b,128,28,28] (conv)[9]

-> [t,b,256,14,14] (conv)[10]
   [t,b,256,14,14] (conv)[11]
   [t,b,256,14,14] (conv)[12]
   [t,b,256,14,14] (conv)[13]

-> [t,b,512,7,7] (conv)[14]
   [t,b,512,7,7] (conv)[15]
   [t,b,512,7,7] (conv)[16]
   [t,b,512,7,7] (conv)[17]

-> [t,b,512,1,1] (avgpool)
   [t,b,512] (flatten)
   [t,b,10] (linear)[18]
   [b,10] (mean)

输出：[b,10]
'''


# 残差块基本单元
class Residual(nn.Module):
    def __init__(self, ch_in, ch_out, stride=1):
        super().__init__()

        self.conv1 = layer.Conv2d(ch_in, ch_out, kernel_size=3, stride=stride, padding=1)
        self.bn1 = layer.BatchNorm2d(ch_out)
        self.activation1 = neuron.IFNode(surrogate_function=surrogate.Sigmoid())
        self.conv2 = layer.Conv2d(ch_out, ch_out, kernel_size=3, stride=1, padding=1)
        self.bn2 = layer.BatchNorm2d(ch_out)
        self.activation2 = neuron.IFNode(surrogate_function=surrogate.Sigmoid())

        # 残差连接
        self.extra = nn.Sequential()  # 不做变化，直接加
        if ch_out != ch_in:  # shape不一，改变shape，再直接加
            self.extra = nn.Sequential(
                layer.Conv2d(ch_in, ch_out, kernel_size=1, stride=stride),
                layer.BatchNorm2d(ch_out)
            )

    def forward(self, x):
        out = self.bn1(self.conv1(x))
        out = self.activation1(out)
        out = self.bn2(self.conv2(out))
        # 残差连接
        out = self.extra(x) + out
        out = self.activation2(out)
        return out


# 大残差块
def ResBlk(ch_in, ch_out, num_residuals, first_block=False):
    blk = []
    for i in range(num_residuals):
        if i == 0 and not first_block:
            # 第一个ch_in,ch_out设置相同
            blk.append(Residual(ch_in, ch_out, stride=2))
        else:
            blk.append(Residual(ch_out, ch_out))
    return blk


# ResNet18
class B_SResNet18(nn.Module):
    def __init__(self, T, in_channels, num_classes):
        super().__init__()

        self.T = T

        self.blk0 = nn.Sequential(
            # conv -> bn -> relu
            layer.Conv2d(in_channels=in_channels, out_channels=64, kernel_size=7, stride=2, padding=3),  # /2
            layer.BatchNorm2d(64),
            neuron.IFNode(surrogate_function=surrogate.Sigmoid()),
            layer.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )
        # 4个大残差块
        # [b, 64, h, w] => [b, 128, h, w]
        self.blk1 = nn.Sequential(
            Residual(64, 64),
            Residual(64, 64),
        )
        # [b, 128, h, w] => [b, 256, h, w]
        self.blk2 = nn.Sequential(
            Residual(64, 128, stride=2),
            Residual(128, 128),
        )
        # [b, 256, h, w] => [b, 512, h, w]
        self.blk3 = nn.Sequential(
            Residual(128, 256, stride=2),
            Residual(256, 256),
        )
        # [b, 512, h, w] => [b, 512, h, w]
        self.blk4 = nn.Sequential(
            Residual(256, 512, stride=2),
            Residual(512, 512),
        )

        self.pool = layer.AdaptiveAvgPool2d((1, 1))
        self.flatten = layer.Flatten()
        self.outlayer = layer.Linear(512, num_classes)

        functional.set_step_mode(self, step_mode='m')

    def forward(self, x): # [b, 3, 224, 224]
        x = x.unsqueeze(0).repeat(self.T, 1, 1, 1, 1)

        # 第一层单独卷积，毕竟没有残差块（1个权重层）
        x = self.blk0(x)
        # 接下是4个大残差块（也就是16个权重层）
        x = self.blk1(x)
        x = self.blk2(x)
        x = self.blk3(x)
        x = self.blk4(x)
        # 自适应池化（后两维变为[1, 1]）
        x = self.pool(x)
        # 转换为[batch, 512]
        x = self.flatten(x)
        # 全连接输出层（1个权重层）
        x = self.outlayer(x)

        x = x.mean(0)
        return x
    def init_weights(self):
        for m in self.modules():
            if isinstance(m, layer.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, layer.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, layer.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

if __name__ == '__main__':
    net = B_SResNet18(4, 3, 10)
    net.init_weights()
    a = torch.randn(50, 3, 224, 224)
    result = net(a)
    print(result.shape)