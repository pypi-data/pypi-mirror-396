import random
import numpy as np
import torch


def set_seed(seed=114514):
    """
        设置随机种子，以确保实验的可重复性

    参数：
        seed:           <int> 随机种子
                        默认为 114514
    """
    #
    random.seed(seed)
    #
    np.random.seed(seed)
    #
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
