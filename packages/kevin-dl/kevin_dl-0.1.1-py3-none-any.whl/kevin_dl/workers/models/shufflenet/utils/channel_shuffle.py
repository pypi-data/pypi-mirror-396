import torch


def channel_shuffle(x, groups):
    bz, c_num, h, w = x.shape
    #
    x = x.view(bz, groups, c_num // groups, h, w)
    # 交换顺序
    x = torch.transpose(x, 1, 2).contiguous()
    # flatten
    x = x.view(bz, -1, h, w)
    return x
