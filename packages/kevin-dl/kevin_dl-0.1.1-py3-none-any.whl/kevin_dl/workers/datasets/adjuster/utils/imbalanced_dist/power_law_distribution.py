import numpy as np


def power_law_distribution(cls_nums, alpha=2.0):
    r"""
        按照幂律分布生成类别样本数的比例。

        公式：
            类别 i (0~cls_nums-1) 在数据集中的占比：
                p_i \propto (i + 1)^{-\alpha}

        参数：
            cls_nums:           <int> 类别总数。
            alpha:              <float> 幂律分布的指数参数，控制分布的陡峭程度。
                                    值越大，分布越陡峭，即长尾效应越明显。
    """
    ranks = np.arange(1, cls_nums + 1)
    res = ranks ** -alpha
    res /= res.sum()
    return res


if __name__ == "__main__":
    proportions = power_law_distribution(cls_nums=10, alpha=2.0)
    print(proportions)
