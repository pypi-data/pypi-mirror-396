import torch
import torch.nn as nn
from kevin_toolbox.computer_science.algorithm import for_dict
from kevin_dl.workers.algorithms.variational_conv import build_conv
from kevin_dl.workers.models.resnet import init_weights, build_blocks
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":resnet:model")
class ResNet(nn.Module):
    def __init__(self, **kwargs):
        """
            resnet

            参数：
                conv:               <dict> 用于设定默认的卷积
                conv_for_stem:      <dict> 用于设定 residual block 中主干 stem 部分的卷积
                conv_for_skip:      <dict> 用于设定 residual block 中 skip connection 部分的卷积
                    当 conv_for_stem 或者 conv_for_skip 不设定时，默认使用 conv 中的设置。
                    支持在 blocks 中进一步设置局部某个 block 的卷积形式，比如：
                        blocks=[
                                    dict(block_num=3, channels_num=64, stride=1, conv_for_stem=...),
                                ]
                    此时局部指定的部分将覆盖掉全局的设置。
        """
        super().__init__()

        # 默认参数
        paras = {
            "type_": None,
            "root": dict(type_="for_cifa"),
            "blocks": None,
            "head": dict(type_="for_cifa"),
            "conv": dict(type_="formal", ),
            "conv_for_stem": None,
            "conv_for_skip": None,
            "block_type": ":resnet:blocks:Basic_Block",
        }

        # 获取参数
        # 以 structures 中的结果为基础，补充设定的部分
        if kwargs.get("type_", None) is not None:
            assert kwargs["type_"] in structures, \
                f'Currently supported model structures are {structures.keys()}, but get a {paras["type_"]}'
            paras.update(structures[kwargs["type_"]])
        # 更新指定的参数
        paras = for_dict.deep_update(stem=paras, patch=kwargs)

        # 校验参数
        #
        for key in ["conv_for_stem", "conv_for_skip"]:
            paras[key] = paras["conv"] if paras[key] is None else paras[key]

        self.paras = paras

        # root
        type_ = self.paras["root"]["type_"]
        conv_ = build_conv(**self.paras["root"].get("conv", self.paras["conv"]))
        if type_ in ["for_cifa", "for_cifa_v1_a", ]:
            self.c_out_last = 64 if type_ == "for_cifa" else 16
            self.root = nn.Sequential(
                conv_(in_channels=3, out_channels=self.c_out_last, kernel_size=3, stride=1, padding=1, bias=False),
                nn.BatchNorm2d(self.c_out_last),
                nn.ReLU(),
            )
        elif type_ in ["for_imagenet", ]:
            self.root = nn.Sequential(
                conv_(in_channels=3, out_channels=64, kernel_size=7, stride=2, padding=3, bias=False),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
            )
            self.c_out_last = 64
        elif type_ in ["for_imagenet_for_type5", ]:
            self.root = nn.Sequential(
                conv_(in_channels=3, out_channels=16, kernel_size=3, stride=2, padding=1, bias=False),
                nn.BatchNorm2d(16),
                conv_(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1, bias=False),
                nn.BatchNorm2d(32),
                conv_(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1, bias=False),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
            )
            self.c_out_last = 64
        elif type_ in ["for_imagenet_for_type5_dw", ]:
            self.root = nn.Sequential(
                conv_(in_channels=3, out_channels=32, kernel_size=1, stride=1, padding=0, bias=False),
                nn.BatchNorm2d(32),
                conv_(in_channels=32, out_channels=32, kernel_size=3, stride=2, padding=1, groups=32, bias=False),
                nn.BatchNorm2d(32),
                conv_(in_channels=32, out_channels=64, kernel_size=1, stride=1, padding=0, bias=False),
                nn.BatchNorm2d(64),
                conv_(in_channels=64, out_channels=64, kernel_size=3, stride=1, padding=1, groups=32, bias=False),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
            )
            self.c_out_last = 64
        else:
            raise ValueError

        # blocks
        self.blocks, self.c_out_last = build_blocks(c_in=self.c_out_last, blocks=self.paras["blocks"],
                                                    block_type=self.paras["block_type"])

        # head
        type_ = self.paras["head"]["type_"]
        # conv_ = build_conv(**self.paras["type_"].get("conv", self.paras["conv"]))
        if type_ in ["for_cifa", "for_cifa_v1_a", ]:
            self.head = nn.Sequential(
                nn.AdaptiveAvgPool2d(1),
                nn.Flatten(),
                nn.Linear(self.c_out_last, paras["head"].get("num_classes", 100)),
            )
        elif type_ in ["for_imagenet", "for_imagenet_for_type5", ]:
            self.head = nn.Sequential(
                nn.AdaptiveAvgPool2d(1),
                nn.Flatten(),
                nn.Linear(self.c_out_last, paras["head"].get("num_classes", 1000)),
            )
        else:
            raise ValueError

        init_weights(self)

    def forward(self, x):
        out = x
        out = self.root(out)
        out = self.blocks(out)
        out = self.head(out)
        return out


structures = dict()

# for imagenet - implement in pytorch
for name, block_num_ls in zip(["ResNet18", "ResNet34"],
                              [[2] * 4, [3, 4, 6, 3]]):
    structures[name] = dict(
        blocks=[
            dict(block_num=block_num_ls[0], c_out=64, stride=1),
            dict(block_num=block_num_ls[1], c_out=128, stride=2),
            dict(block_num=block_num_ls[2], c_out=256, stride=2),
            dict(block_num=block_num_ls[3], c_out=512, stride=2),
        ],
        block_type=":resnet:blocks:Basic_Block",
    )
for name, block_num_ls in zip(["ResNet50", "ResNet101", "ResNet152"],
                              [[3, 4, 6, 3], [3, 4, 23, 3], [3, 8, 36, 3]]):
    structures[name] = dict(
        blocks=[
            dict(block_num=block_num_ls[0], c_out=64, stride=1),
            dict(block_num=block_num_ls[1], c_out=128, stride=2),
            dict(block_num=block_num_ls[2], c_out=256, stride=2),
            dict(block_num=block_num_ls[3], c_out=512, stride=2),
        ],
        block_type=":resnet:blocks:Pre_Act_Bottle_Neck_Block",
    )

# for cifa-10/100 - implement in Deep Residual Learning for Image Recognition. arXiv:1512.03385
for name, block_num_ls in zip(["ResNet20_v1_a", "ResNet32_v1_a", "ResNet44_v1_a",
                               "ResNet56_v1_a", "ResNet110_v1_a", "ResNet1202_v1_a"],
                              [[3] * 3, [5] * 3, [7] * 3, [9] * 3, [18] * 3, [200] * 3]):
    structures[name] = dict(
        root=dict(type_="for_cifa_v1_a"),
        blocks=[
            dict(block_num=block_num_ls[0], c_out=16, stride=1, type_of_skip="v1_a"),
            dict(block_num=block_num_ls[1], c_out=32, stride=2, type_of_skip="v1_a"),
            dict(block_num=block_num_ls[2], c_out=64, stride=2, type_of_skip="v1_a"),
        ],
        head=dict(type_="for_cifa_v1_a"),
        block_type=":resnet:blocks:Basic_Block",
    )


def _test():
    from torch.autograd import Variable
    from kevin_dl.utils import count_parameter_nums_of_model, count_flops_of_model
    # from line_profiler import LineProfiler

    # net = ResNet(
    #     type_="ResNet18",
    #     block_type="PreActBlock",
    #     conv=dict(
    #         type_="variational",
    #         setting_for_refactor=dict(mode="unitary", setting_for_cal_norm=dict(ord=2)),
    #         setting_for_basic=dict(
    #             amp_ratio=2.0,
    #             groups=10,
    #         ),
    #         setting_for_coeff=dict(
    #             amp_ratio=2.0,
    #             groups=1,
    #             initializer="lambda x: torch.nn.init.orthogonal_(x, gain=1)",
    #         )
    #     ),
    # )

    net = ResNet(
        type_="ResNet18",
        root=dict(type_="for_imagenet_for_type5_dw"),
        head=dict(type_="for_imagenet_for_type5")
    )

    # lp = LineProfiler()
    # lp_wrapper = lp(ResNet)
    # lp_wrapper(type_="ResNet18", block_type="PreActBlock", conv=dict(type_="variational", ), )
    # lp.print_stats()

    print(net)
    print(count_parameter_nums_of_model(net))
    print(count_flops_of_model(net, (3, 224, 224)) / 1e6)
    y = net(Variable(torch.randn(1, 3, 224, 224)))
    print(y.size())


if __name__ == '__main__':
    _test()
