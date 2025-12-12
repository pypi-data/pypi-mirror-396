import torch
import torch.nn as nn
from torch.autograd import Variable
from kevin_toolbox.computer_science.algorithm import for_dict
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":vgg:model")
class VGG(nn.Module):
    """
        VGG 网络

        参考：
            1. 原论文配置： https://pic4.zhimg.com/80/v2-45797c0bde15ceb296eb2a062b494183_720w.webp
            2. https://github.com/GustavoStahl/VGG16-CIFAR100-Pytorch/blob/master/vgg16.py
            3. https://github.com/geifmany/cifar-vgg/blob/master/cifar100vgg.py
            4. torchvision.models.VGG 官方实现
    """

    def __init__(self, **kwargs):
        super(VGG, self).__init__()

        # 默认参数
        paras = {
            "type_": None,
            "root": dict(c_in=3, ),
            "blocks": None,
            "head": dict(type_="for_cifa", num_classes=100, dropout=0.5),
            "block_type": ":vgg:blocks:Basic_Block"
        }

        # 获取参数
        # 以 structures 中的结果为基础，补充设定的部分
        if kwargs.get("type_", None) is not None:
            assert kwargs["type_"] in structures, \
                f'Currently supported model structures are {structures.keys()}, but get a {paras["type_"]}'
            paras.update(structures[kwargs["type_"]])
        # 更新指定的参数
        paras = for_dict.deep_update(stem=paras, patch=kwargs)

        # root
        if paras["root"]["type_"] == "for_mnist":
            paras["root"] = dict(c_in=1)

        # blocks
        self.blocks = nn.Sequential()
        c_last = paras["root"]["c_in"]
        for g_id, cfg in enumerate(paras["blocks"]):
            assert "c_in" not in cfg, \
                f'para c_in is not allowed in the cfg of blocks'
            block_builder = MODELS.get(name=cfg.get("block_type", paras["block_type"]))
            #
            block = block_builder(c_in=c_last, **cfg)
            c_last = block.c_last
            self.blocks.add_module(f'group_{g_id}', block)

        # head
        if paras["head"]["type_"] in ["for_cifa", "for_cifar"]:
            self.head = nn.Sequential(
                nn.AvgPool2d(kernel_size=1, stride=1),
                nn.Flatten(),
                nn.Linear(c_last, out_features=2048),
                nn.ReLU(),
                nn.Dropout(p=paras["head"]["dropout"]),
                nn.Linear(in_features=2048, out_features=paras["head"]["num_classes"])
            )
        elif paras["head"]["type_"] == "for_imagenet":
            self.head = nn.Sequential(
                nn.AdaptiveAvgPool2d((7, 7)),
                nn.Flatten(),
                nn.Linear(512 * 7 * 7, out_features=4096),
                nn.ReLU(),
                nn.Dropout(p=paras["head"]["dropout"]),
                nn.Linear(in_features=4096, out_features=4096),
                nn.ReLU(),
                nn.Dropout(p=paras["head"]["dropout"]),
                nn.Linear(in_features=4096, out_features=paras["head"]["num_classes"])
            )
        else:
            raise NotImplementedError
        self._initialize_weights()

    def forward(self, x):
        out = self.blocks(x)
        out = self.head(out)
        return out

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)


structures = {
    'VGG11': dict(blocks=[
        dict(cnn_num=1, c_out=64, stride=2),
        dict(cnn_num=1, c_out=128, stride=2),
        dict(cnn_num=2, c_out=256, stride=2),
        dict(cnn_num=2, c_out=512, stride=2),
        dict(cnn_num=2, c_out=512, stride=2)
    ]),
    'VGG13': dict(blocks=[
        dict(cnn_num=2, c_out=64, stride=2),
        dict(cnn_num=2, c_out=128, stride=2),
        dict(cnn_num=2, c_out=256, stride=2),
        dict(cnn_num=2, c_out=512, stride=2),
        dict(cnn_num=2, c_out=512, stride=2)
    ]),
    'VGG16': dict(blocks=[
        dict(cnn_num=2, c_out=64, stride=2),
        dict(cnn_num=2, c_out=128, stride=2),
        dict(cnn_num=3, c_out=256, stride=2),
        dict(cnn_num=3, c_out=512, stride=2),
        dict(cnn_num=3, c_out=512, stride=2)
    ]),
    'VGG19': dict(blocks=[
        dict(cnn_num=2, c_out=64, stride=2),
        dict(cnn_num=2, c_out=128, stride=2),
        dict(cnn_num=4, c_out=256, stride=2),
        dict(cnn_num=4, c_out=512, stride=2),
        dict(cnn_num=4, c_out=512, stride=2)
    ])
}

if __name__ == "__main__":
    import os

    # # 设置环境变量
    # os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

    from kevin_dl.deploy import convert_torch_to_onnx

    # from kevin_dl.deploy.convert_torch_to_caffe import convert_torch_to_caffe

    net = VGG(type_='VGG11', block_type=":vgg:blocks:Rotation_Invariant_Block")
    x = torch.randn(2, 3, 32, 32)
    print(net(Variable(x)).size())
    print(net)

    output_dir = os.path.join("../", "vgg11_model_2")
    os.makedirs(output_dir, exist_ok=True)
    convert_torch_to_onnx(model=net, inputs=x, output_dir=output_dir)
    # import torchvision.models as models
    #
    # models.vgg11()
