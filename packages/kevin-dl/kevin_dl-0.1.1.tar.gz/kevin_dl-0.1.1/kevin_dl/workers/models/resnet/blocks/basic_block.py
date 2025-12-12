import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from kevin_toolbox.patches.for_torch.nn import Lambda_Layer
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":resnet:blocks:Basic_Block")
class Basic_Block(nn.Module):

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
                norm_for_skip:      <callable> skip connection 短连接部分使用的 normalize 函数
                type_of_skip:       <str> skip connection 短连接的类型
                                        目前支持：
                                            "default":      使用 1x1 卷积
                                            "v1_a":         对于xy方向，间隔 stride 进行取值；对于channel，在前后填充0

            工作流程：
                    inputs:[bz, c_in, m, n]
                            ||======================================++
                            ||                                      ||
                conv:[c_in,c_out,k,k] no bias, stride=s             ||     skip connection("default"):
                            ||                                      ||
                            bn                                      ||
                            ||                       conv:[c_in,c_out_real,1,1] no bias, stride=s
                           relu                                     ||
                            ||                                      bn
                conv:[c_out,c_out_real,k,k] no bias, stride=1       ||
                            ||                                      ||
                            bn                                      ||
                            ||                                      ||
                          (add) <===================================++
                            ||
                           relu
                            ||
                    outputs:[bz, c_out_real, ceil(m/s), ceil(n/s)]
        """
        super(Basic_Block, self).__init__()

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
            #
            "conv_for_stem": nn.Conv2d,
            "conv_for_skip": nn.Conv2d,
            "norm_for_stem": nn.BatchNorm2d,
            "norm_for_skip": nn.BatchNorm2d,
            "type_of_skip": "default",
        }

        # 获取参数
        p.update(kwargs)

        # 校验参数
        assert p["type_of_skip"] in ("default", "v1_a")
        assert p["c_in"] is not None and p["c_out"] is not None
        if p["c_out_real"] is None:
            p["c_out_real"] = math.ceil(p["c_out"] * p["expansion"])
        padding = int((p["kernel_size"] - 1) / 2)

        # 网络
        self.conv1 = p["conv_for_stem"](in_channels=p["c_in"], out_channels=p["c_out"],
                                        kernel_size=p["kernel_size"], stride=p["stride"], padding=padding,
                                        bias=False)
        self.bn1 = p["norm_for_stem"](p["c_out"])
        self.conv2 = p["conv_for_stem"](in_channels=p["c_out"], out_channels=p["c_out_real"],
                                        kernel_size=p["kernel_size"], stride=1, padding=padding,
                                        bias=False)
        self.bn2 = p["norm_for_stem"](p["c_out_real"])

        self.shortcut = nn.Sequential()
        if p["stride"] != 1 or p["c_in"] != p["c_out_real"]:
            if p["type_of_skip"] == "v1_a":
                gap = p["c_out_real"] - p["c_in"]
                assert gap >= 0
                self.shortcut = Lambda_Layer(
                    func=lambda x: F.pad(x[:, :, ::p["stride"], ::p["stride"]],
                                         (0, 0, 0, 0, gap // 2, gap - gap // 2), mode="constant", value=0))
            else:
                self.shortcut = nn.Sequential(
                    p["conv_for_skip"](in_channels=p["c_in"], out_channels=p["c_out_real"], kernel_size=1,
                                       stride=p["stride"],
                                       bias=False),
                    p["norm_for_skip"](p["c_out_real"])
                )
        #
        self.paras = p

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out


if __name__ == '__main__':
    a = torch.randn(10, 3, 5, 5)
    layer = Basic_Block(c_in=3, c_out=3, stride=2, type_of_skip="v1_a", norm_for_skip=nn.InstanceNorm2d)
    print(layer(a).shape)

    layer_2 = MODELS.get(name=":resnet:blocks:Basic_Block")(c_in=3, c_out=3, stride=2, type_of_skip="v1_a",
                                                            norm_for_skip=nn.InstanceNorm2d)
    print(layer_2(a).shape)
