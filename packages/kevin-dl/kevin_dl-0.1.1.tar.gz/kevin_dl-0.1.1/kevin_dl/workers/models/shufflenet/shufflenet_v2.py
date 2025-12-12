import torch
import torch.nn as nn
from kevin_toolbox.computer_science.algorithm import for_dict
from kevin_dl.workers.models.shufflenet import init_weights, build_blocks
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":shufflenet:ShuffleNet_v2")
class ShuffleNet_v2(nn.Module):
    def __init__(self, **kwargs):
        """
            ShuffleNet_v2

            参数：
        """
        super(ShuffleNet_v2, self).__init__()

        # 默认参数
        p = {
            "type_": None,
            "root": dict(type_="for_imagenet", c_out=24),
            "blocks": None,
            "head": dict(type_="for_imagenet", c_out=1024, num_classes=1000),
            "block_type": ":shufflenet:blocks:Inverted_Residual",
        }

        # 获取参数
        # 以 structures 中的结果为基础，补充设定的部分
        if kwargs.get("type_", None) is not None:
            assert kwargs["type_"] in structures, \
                f'Currently supported model structures are {structures.keys()}, but get a {p["type_"]}'
            p.update(structures[kwargs["type_"]])
        # 更新指定的参数
        p = for_dict.deep_update(stem=p, patch=kwargs)

        self.c_out_last = None
        # root
        if p["root"]["type_"] in ["for_imagenet", "for_imagenet_for_type5", ]:
            temp = [
                nn.Conv2d(in_channels=3, out_channels=p["root"]["c_out"], kernel_size=3, stride=2,
                          padding=1, bias=False),
                nn.BatchNorm2d(p["root"]["c_out"]),
                nn.ReLU()
            ]
            if p["root"]["type_"] == "for_imagenet_for_type5":
                temp.append(nn.MaxPool2d(kernel_size=2, stride=2, padding=0))
            else:
                temp.append(nn.MaxPool2d(kernel_size=3, stride=2, padding=1))
            self.root = nn.Sequential(*temp)
            self.c_out_last = p["root"]["c_out"]
        else:
            raise NotImplemented(f'root {p["root"]["type_"]} is not supported')

        # blocks
        self.blocks, self.c_out_last = build_blocks(c_in=self.c_out_last, blocks=p["blocks"],
                                                    block_type=p["block_type"])

        # head
        if p["head"]["type_"] in ["for_imagenet", ]:
            self.head = nn.Sequential(
                nn.Conv2d(in_channels=self.c_out_last, out_channels=p["head"]["c_out"], kernel_size=1, stride=1,
                          padding=0,
                          bias=False),
                nn.BatchNorm2d(p["head"]["c_out"]),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(1),
                nn.Flatten(),
                nn.Linear(p["head"]["c_out"], out_features=p["head"]["num_classes"], bias=True),
            )
            self.c_out_last = p["head"]["num_classes"]
        else:
            raise NotImplemented(f'head {p["head"]["type_"]} is not supported')

        init_weights(self)

        self.paras = p

    def forward(self, x):
        x = self.root(x)
        x = self.blocks(x)
        out = self.head(x)
        return out


# for imagenet - implement in pytorch
structures = dict()
block_num_ls = [4, 8, 4]
for name, c_out_ls in zip(["0.5x", "1.0x", "1.5x", "2.0x"],
                          [
                              [24, 48, 96, 192, 1024],
                              [24, 116, 232, 464, 1024],
                              [24, 176, 352, 704, 1024],
                              [24, 244, 488, 976, 2048]
                          ]):
    structures[name] = dict(
        root=dict(type_="for_imagenet", c_out=c_out_ls[0]),
        blocks=[
            dict(block_num=block_num, c_out=c_out, stride=2, c_out_mid=c_out // 2,
                 c_out_skip=c_out // 2, ) for block_num, c_out in zip(block_num_ls, c_out_ls[1:])
        ],
        head=dict(type_="for_imagenet", num_classes=1000, c_out=c_out_ls[-1]),
        block_type=":shufflenet:blocks:Inverted_Residual",
    )

if __name__ == "__main__":
    model = ShuffleNet_v2(type_="2.0x")
    print(model)

    test_data = torch.rand(5, 3, 224, 224)
    test_outputs = model(test_data)
    print(test_outputs.size())
