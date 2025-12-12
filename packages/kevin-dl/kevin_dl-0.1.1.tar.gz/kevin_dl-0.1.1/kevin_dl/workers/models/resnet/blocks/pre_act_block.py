import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":resnet:blocks:Pre_Act_Block")
class Pre_Act_Block(nn.Module):
    """
        Pre-activation version of the Basic_Block.
    """

    def __init__(self, **kwargs):
        """
            参数：
                c_in, c_out:        <int> 输入输出 channel 数
                expansion:          <float> 对原定输出的放大倍数
                                        默认是 1
                                        注意，真正的输出 channel 数应该是 c_out_real = ceil(c_out * expansion)
                c_out_real:         <int> 当设定改值时，默认覆盖 expansion 的设置
                stride:             <int>
                kernel_size:        <int>
                conv_for_stem:      <callable> stem 部分使用的卷积函数
                conv_for_skip:      <callable> skip connection 短连接部分使用的卷积函数
                norm_for_stem:      <callable> stem 部分使用的 normalize 函数

            工作流程：
                    inputs:[bz, c_in, m, n]
                            ||
                            bn
                            ||
                           relu
                            ||
                            ++======================================++
                            ||                                      ||
            conv:[c_in,c_out,k,k] no bias, stride=s                 ||
                            ||                                      ||
                            bn                                      ||
                            ||                                      ||
                           relu                    conv:[c_in,c_out_real,1,1] no bias, stride=s
                            ||                                      ||
                conv:[c_out,c_out_real,k,k] no bias, stride=1       ||
                            ||                                      ||
                          (add) <===================================++
                            ||
            outputs:[bz, c_out_real, ceil(m/s), ceil(n/s)]
        """
        super(Pre_Act_Block, self).__init__()

        # 默认参数
        p = {
            # 必要参数
            "c_in": None,
            "c_out": None,
            "c_out_real": None,
            #
            "expansion": 1,
            "kernel_size": 3,
            "stride": 1,
            "conv_for_stem": nn.Conv2d,
            "conv_for_skip": nn.Conv2d,
            "norm_for_stem": nn.BatchNorm2d
        }

        # 获取参数
        p.update(kwargs)

        # 校验参数
        assert p["c_in"] is not None and p["c_out"] is not None
        if p["c_out_real"] is None:
            p["c_out_real"] = math.ceil(p["c_out"] * p["expansion"])
        padding = int((p["kernel_size"] - 1) / 2)

        # 网络
        self.bn1 = p["norm_for_stem"](p["c_in"])
        self.conv1 = p["conv_for_stem"](in_channels=p["c_in"], out_channels=p["c_out"],
                                        kernel_size=p["kernel_size"], stride=p["stride"], padding=padding,
                                        bias=False)
        self.bn2 = p["norm_for_stem"](p["c_out"])
        self.conv2 = p["conv_for_stem"](in_channels=p["c_out"], out_channels=p["c_out_real"],
                                        kernel_size=p["kernel_size"], stride=1, padding=padding,
                                        bias=False)

        self.shortcut = nn.Sequential()
        if p["stride"] != 1 or p["c_in"] != p["c_out_real"]:
            self.shortcut = nn.Sequential(
                p["conv_for_skip"](in_channels=p["c_in"], out_channels=p["c_out_real"], kernel_size=1,
                                   stride=p["stride"],
                                   bias=False),
            )

        #
        self.paras = p

    def forward(self, x):
        out = F.relu(self.bn1(x))
        shortcut = self.shortcut(out)
        out = self.conv1(out)
        out = self.conv2(F.relu(self.bn2(out)))
        out += shortcut
        return out


if __name__ == '__main__':
    a = torch.randn(10, 3, 6, 6)
    layer = Pre_Act_Block(c_in=3, c_out=3, expansion=3, stride=3)
    print(layer(a).shape)
