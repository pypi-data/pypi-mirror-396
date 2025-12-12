import numpy as np


def exponential_decay_distribution(cls_nums, gamma=1 / 10):
    r"""
        类别样本数按照指数下降

        公式：
            类别 i (0~cls_nums-1)在数据集中的占比：
                p_i \propto gamma^{i/(cls_nums-1)}

        参数：
            gamma:              <float> 失衡因子。
                                    0~1 之间，越大越平衡。
    """
    res = np.asarray([gamma ** (i / (cls_nums - 1)) for i in range(cls_nums)])
    res /= res.sum()
    return res


if __name__ == "__main__":
    print(exponential_decay_distribution(cls_nums=10, gamma=0.5))
