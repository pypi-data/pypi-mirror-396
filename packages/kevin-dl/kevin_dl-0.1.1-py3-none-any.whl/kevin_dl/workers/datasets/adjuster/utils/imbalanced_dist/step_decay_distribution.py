import math
import numpy as np


def step_decay_distribution(cls_nums, step_width=2, decay_ratio=0.5, b_relative=True):
    r"""
        按照阶梯式衰减生成类别样本比例分布。

        公式：
            对于类别 i (0~cls_nums-1)，其所属阶梯 k 为：
                k = i // step_width
            则该类别的占比满足：
                当 b_relative=True 时，为 p_i \propto (1-decay_ratio)^k
                当 b_relative=False 时，为 p_i \propto max(1 - decay_ratio*k, 0)
            最后对所有 p_i 进行归一化处理，使得 sum(p_i) = 1。

        参数：
            cls_nums:           <int> 类别总数。
            step_width:         <int/float> 每个阶梯包含的类别数。
                                    当设置为小于 1.0 时，将解释为 step_width=math.ceil(step_width*cls_nums)
            decay_ratio:        <float> 每个阶梯之间的比例衰减因子，取值越小，不平衡程度越高。
    """
    assert step_width > 0
    if step_width < 1.0:
        step_width = math.ceil(step_width * cls_nums)
    if b_relative:
        proportions = np.array([decay_ratio ** (i // step_width) for i in range(cls_nums)])
    else:
        proportions = np.array([max(1 - decay_ratio * (i // step_width), 0) for i in range(cls_nums)])
    proportions /= proportions.sum()
    return proportions


if __name__ == "__main__":
    # 示例：10个类别，每2个类别为一阶梯，衰减因子为0.5
    print(step_decay_distribution(cls_nums=10, step_width=3, decay_ratio=0.5, b_relative=False))
