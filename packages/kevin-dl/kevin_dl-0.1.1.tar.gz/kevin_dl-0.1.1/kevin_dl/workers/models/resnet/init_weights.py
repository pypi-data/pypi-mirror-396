import torch
import torch.nn as nn


def init_weights(model):
    for sub_model in model.children():
        if callable(getattr(sub_model, "init_weights", None)):
            sub_model.init_weights()
        elif isinstance(sub_model, nn.Conv2d):
            nn.init.kaiming_normal_(sub_model.weight, mode="fan_out", nonlinearity="relu")
        elif isinstance(sub_model, (nn.BatchNorm2d, nn.GroupNorm)):
            nn.init.constant_(sub_model.weight, 1)
            nn.init.constant_(sub_model.bias, 0)
        else:
            init_weights(sub_model)
