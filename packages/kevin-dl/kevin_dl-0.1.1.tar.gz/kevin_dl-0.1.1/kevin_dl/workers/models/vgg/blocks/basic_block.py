import math
import torch.nn as nn
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":vgg:blocks:Basic_Block")
class Basic_Block(nn.Module):
    def __init__(self, **kwargs):
        super(Basic_Block, self).__init__()

        # 默认参数
        p = {
            # 必要参数
            "c_in": None,
            "c_out": None,
            #
            "kernel_size": 3,
            "stride": 2,
            #
            "cnn_num": 2,
            "b_use_bn": True,
            "dropout": None,
        }

        # 获取参数
        p.update(kwargs)

        # 校验参数
        assert p["c_in"] is not None and p["c_out"] is not None
        c_in_ls = p["c_in"] if isinstance(p["c_in"], (list, tuple)) else [p["c_in"]] * p["cnn_num"]
        c_out_ls = p["c_out"] if isinstance(p["c_out"], (list, tuple)) else c_in_ls[1:] + [p["c_out"]]
        assert c_in_ls[1:] == c_out_ls[:-1]

        # 网络
        layers = []
        for i in range(p["cnn_num"]):
            layers += [
                nn.Conv2d(in_channels=c_in_ls[i], out_channels=c_out_ls[i], kernel_size=p["kernel_size"],
                          padding=math.ceil(p["kernel_size"] / 2) - 1, stride=1, bias=not p["b_use_bn"])
            ]
            if p["b_use_bn"]:
                layers += [nn.BatchNorm2d(num_features=c_out_ls[i])]
            layers += [
                nn.ReLU()
            ]
            if p["dropout"] is not None and p["dropout"] > 0.:
                layers += [nn.Dropout(p=p["dropout"])]
        self.conv = nn.Sequential(*layers)
        self.pooling = nn.MaxPool2d(kernel_size=p["stride"], stride=p["stride"])

        #
        self.c_last = c_out_ls[-1]
        self.paras = p

    def forward(self, x):
        return self.pooling(self.conv(x))
