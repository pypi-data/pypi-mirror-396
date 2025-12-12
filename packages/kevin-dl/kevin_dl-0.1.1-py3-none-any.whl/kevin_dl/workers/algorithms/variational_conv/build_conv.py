import torch.nn as nn

_args_name = ["in_channels", "out_channels", "kernel_size", "stride", "padding", "dilation", "groups", "bias",
              "padding_mode", "device", "dtype"]


def build_conv(type_="formal", **kwargs):
    if type_ == "formal":
        conv_builder = nn.Conv2d
    elif type_ == "variational":
        from kevin_dl.workers.algorithms.variational_conv import Variational_Conv
        def func(*conv_args, **conv_paras):
            # 将 conv_args 中参数转换为 paras dict 并添加到 conv_paras
            for i, v in enumerate(conv_args):
                assert _args_name[i] not in conv_paras
                conv_paras[_args_name[i]] = v
            return Variational_Conv(conv_paras=conv_paras, **kwargs)

        conv_builder = func
    else:
        print(type_)
        raise ValueError
    return conv_builder
