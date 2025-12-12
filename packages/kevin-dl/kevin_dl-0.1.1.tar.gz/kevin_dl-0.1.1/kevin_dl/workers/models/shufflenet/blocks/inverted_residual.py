import torch
import torch.nn as nn
from kevin_dl.workers.models.shufflenet.utils import channel_shuffle
from kevin_dl.workers.variable import MODELS
from kevin_dl.workers.models.shufflenet.blocks import Inverted_Residual_wout_Stride, Inverted_Residual_with_Stride


@MODELS.register(name=":shufflenet:blocks:Inverted_Residual")
def build_inverted_residual(**kwargs):
    if kwargs.get("stride", 1) == 1:
        return Inverted_Residual_wout_Stride(**kwargs)
    else:
        return Inverted_Residual_with_Stride(**kwargs)


if __name__ == '__main__':
    print(MODELS.get(name=":shufflenet:blocks:Inverted_Residual")(c_in=11, c_out=20, c_out_mid=8, kernel_size=3))
