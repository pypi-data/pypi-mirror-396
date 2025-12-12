import torch.nn as nn
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":toy_model:Multi_Layer_FC")
class Multi_Layer_FC(nn.Module):
    """
        多层全连接网络
    """

    def __init__(self, **kwargs):
        """
            参数：
                input_size:                 <int> 输入尺寸
                layer_size_ls:              <list of int> 一个列表，每个元素为每一隐藏层的输出大小
                b_bias:                     <boolean> 是否使用偏置项。
                                                默认 True
                activation_type:           <str> 激活函数的类型。
                                                默认 ReLU
        """
        super().__init__()
        paras = {
            #
            "input_size": None,
            "layer_size_ls": None,
            #
            "b_bias": True,
            "activation_type": "ReLU"
        }
        paras.update(kwargs)
        assert isinstance(paras["layer_size_ls"], (list, tuple,)) and len(paras["layer_size_ls"]) > 0
        act_func = getattr(nn, paras["activation_type"])

        layers = []
        n_in = paras["input_size"]
        # 构造各个隐藏层：线性层 + ReLU 激活
        for i, n_out in enumerate(paras["layer_size_ls"]):
            layers.append(nn.Linear(in_features=n_in, out_features=n_out, bias=paras["b_bias"]))
            if i < len(paras["layer_size_ls"]) - 1:
                layers.append(act_func())
                n_in = n_out
        self.stem = nn.Sequential(*layers)

        self.paras = paras

    def forward(self, x):
        # flatten
        x = x.view(x.size(0), -1)
        out = self.stem(x)
        return out



if __name__ == "__main__":
    import torch

    x_ = torch.randn(2, 10, 32)
    paras_ = {
        "input_size": 320,
        "layer_size_ls": [128, 64, 32, 16],
        "b_bias": True,
        "activation_type": "ReLU"
    }
    model = Multi_Layer_FC(**paras_)
    print(model)
    print(model(x_).shape)
