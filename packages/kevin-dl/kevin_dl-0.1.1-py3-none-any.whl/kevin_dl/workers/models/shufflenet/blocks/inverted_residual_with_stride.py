import torch
import torch.nn as nn
from kevin_dl.workers.models.shufflenet.utils import channel_shuffle
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":shufflenet:blocks:Inverted_Residual_with_Stride")
class Inverted_Residual_with_Stride(nn.Module):

    def __init__(self, **kwargs):
        """
            参数：
                c_in, c_out:        <int> 输入输出 channel 数
                c_out_mid:          <int>
                c_out_skip:         <int>
                kernel_size:        <int>
                stride:             <int>

            工作流程：

                    inputs:[bz, c_in, m, n]
                            ||
                            ||                                          c_out_skip = c_in（默认）
                            ||======================================++  c_out_stem = c_out - c_out_skip
                            ||                                      ||
                conv:[c_in,c_out_mid,1,1] no bias, stride=1         ||
                            ||                                      ||
                            bn             depth_wise_conv:[c_in,c_in,k,k] no bias, stride=s
                            ||                                      ||
                           relu                                     ||
                            ||                                      bn
    depth_wise_conv:[c_out_mid,c_out_mid,k,k] no bias, stride=s     ||
                            ||                                      ||
                            bn                  conv:[c_in,c_out_skip,1,1] no bias, stride=1
                            ||                                      ||
                conv:[c_out_mid,c_out_stem,1,1] no bias, stride=1   ||
                            ||                                      ||
                            bn                                      bn
                            ||                                      ||
                           relu                                    relu
                            ||                                      ||
                          (concat) <================================++
                            ||
                     (channel_shuffle)
                            ||
                    outputs:[bz, c_out, m, n]
        """
        super(Inverted_Residual_with_Stride, self).__init__()

        # 默认参数
        p = {
            # 必要参数
            "c_in": None,
            "c_out": None,
            "c_out_mid": None,
            "c_out_skip": None,
            #
            "kernel_size": 3,
            "stride": 2
        }

        # 获取参数
        p.update(kwargs)

        # 校验参数
        if p["c_out_skip"] is None:
            p["c_out_skip"] = p["c_in"]
        c_out_stem = p["c_out"] - p["c_out_skip"]
        assert p["c_out"] % 2 == 0

        # stem
        self.stem = nn.Sequential(
            #
            nn.Conv2d(in_channels=p["c_in"], out_channels=p["c_out_mid"], kernel_size=1, stride=1, padding=0,
                      bias=False),
            nn.BatchNorm2d(p["c_out_mid"]),
            nn.ReLU(),
            # depth_wise_conv
            nn.Conv2d(in_channels=p["c_out_mid"], out_channels=p["c_out_mid"], kernel_size=p["kernel_size"],
                      stride=p["stride"], padding=p["kernel_size"] // 2, groups=p["c_out_mid"], bias=False),
            nn.BatchNorm2d(p["c_out_mid"]),
            #
            nn.Conv2d(in_channels=p["c_out_mid"], out_channels=c_out_stem, kernel_size=1, stride=1, padding=0,
                      bias=False),
            nn.BatchNorm2d(c_out_stem),
            nn.ReLU(),
        )

        self.skip = nn.Sequential(
            # depth_wise_conv
            nn.Conv2d(in_channels=p["c_in"], out_channels=p["c_in"], kernel_size=p["kernel_size"],
                      stride=p["stride"], padding=p["kernel_size"] // 2, groups=p["c_in"], bias=False),
            nn.BatchNorm2d(p["c_in"]),
            #
            nn.Conv2d(in_channels=p["c_in"], out_channels=p["c_out_skip"], kernel_size=1, stride=1, padding=0,
                      bias=False),
            nn.BatchNorm2d(p["c_out_skip"]),
            nn.ReLU(),
        )
        self.paras = p

    def forward(self, x):
        #
        out_skip = self.skip(x)
        out_stem = self.stem(x)
        # concat
        out = torch.cat((out_skip, out_stem), dim=1)
        # channel_shuffle
        out = channel_shuffle(out, groups=2)
        return out


if __name__ == '__main__':
    print(Inverted_Residual_with_Stride(c_in=11, c_out=20, c_out_mid=8, kernel_size=3, stride=2))
