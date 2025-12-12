import torch.nn as nn
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":toy_model:Conv_Pool_FC_Net")
class Conv_Pool_FC_Net(nn.Module):
    """
        自定义卷积网络结构

        参数：
            input_channel:          <int> 输入通道数（如 MNIST 是 1）
            conv_layers:            <list of dict/int> 每一层卷积的参数配置
                                        当其形式为 list of dict 时，输入应形如：
                                        [
                                            {"out_channels": 32, ("kernel_size": 3, "padding": 1, "stride": 2, "b_use_pooling": True)},
                                           ...
                                        ]
                                        括号内是默认值，可以不额外指定。
                                        当其形式为 list of int 时， 表示指定的是每个卷积层的 out_channels，此时其余参数使用默认值。
            fc_layers:              <list of dict/int> 每一层fc的参数配置
            fc_output_size:         <int> 全连接层的输出大小，默认 128
            num_classes:            <int> 最终分类数量，默认 10
    """

    def __init__(self, **kwargs):
        super().__init__()

        paras = {
            "in_channels": 1,
            "conv_layers": [32, 64],
            "fc_layers": [128, ],
            "num_classes": 10
        }
        paras.update(kwargs)
        assert isinstance(paras["conv_layers"], (list, tuple)) and len(paras["conv_layers"]) > 0
        temp = []
        for it in paras["conv_layers"]:
            if not isinstance(it, dict):
                it = {"out_channels": it}
            it.setdefault("kernel_size", 3)
            it.setdefault("padding", 1)
            it.setdefault("stride", 2)
            it.setdefault("b_use_pooling", True)
            temp.append(it)
        paras["conv_layers"] = temp
        #
        temp = []
        for it in paras["fc_layers"]:
            if not isinstance(it, dict):
                it = {"out_nums": it}
            it.setdefault("dropout", None)
            temp.append(it)
        paras["fc_layers"] = temp

        layers = []
        in_channels = paras["in_channels"]
        for it in paras["conv_layers"]:
            layers.extend([
                nn.Conv2d(in_channels=in_channels, out_channels=it["out_channels"], kernel_size=it["kernel_size"],
                          padding=it["padding"], stride=it["stride"] if not it["b_use_pooling"] else 1, bias=False),
                nn.BatchNorm2d(it["out_channels"]),
                nn.ReLU()
            ])
            if it["b_use_pooling"]:
                layers.append(nn.MaxPool2d(kernel_size=it["stride"], stride=it["stride"]))
            in_channels = it["out_channels"]
        self.feature_extractor = nn.Sequential(*layers)

        layers = [
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        ]
        in_nums = in_channels
        for it in paras["fc_layers"]:
            layers.extend([
                nn.Linear(in_nums, it["out_nums"]),
                nn.ReLU(inplace=True),
            ])
            if it["dropout"] is not None:
                layers.append(nn.Dropout(it["dropout"]))
            in_nums = it["out_nums"]
        self.classifier = nn.Sequential(
            *layers,
            nn.Linear(in_nums, paras["num_classes"])
        )

        self.paras = paras

    def forward(self, x):
        x = self.feature_extractor(x)
        x = self.classifier(x)
        return x


if __name__ == "__main__":
    import torch

    paras_ = {
        "in_channels": 1,
        "conv_layers": [32, 64],
        "fc_layers": [128, ],
        "num_classes": 10
    }
    model = Conv_Pool_FC_Net(**paras_)
    print(model)
    dummy_input = torch.randn(2, 1, 28, 28)
    output = model(dummy_input)
    print("Output shape:", output.shape)
