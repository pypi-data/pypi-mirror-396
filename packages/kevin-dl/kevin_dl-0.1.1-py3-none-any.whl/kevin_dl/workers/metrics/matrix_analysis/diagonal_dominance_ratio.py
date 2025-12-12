import numpy as np


def diagonal_dominance_ratio(matrix, axis=0, reduction='none', b_abs=True, eps=1e-12):
    """
        计算对角占优度（Diagonal Dominance Ratio）

        公式：
            按照 axis=1 计算：
                rho_i = |a_ii| / (sum_{j != i} |a_ij|)
            按照所有对角线元素进行计算：
                rho = sum_{i}|a_ii| / sum_{i}(sum_{j != i} |a_ij|)

        参数：
            axis:           <int> 沿着哪个轴进行计算。
            reduction:      <str> 使用何种方式得到全局指标
                            目前支持以下几种模式：
                                - 'mean':       先对给定axis进行处理，然后返回全局平均值
                                - 'min':        先对给定axis进行处理，然后返回全局最小值
                                - 'none':       返回每个axis的指标
                                - 'all':        按照对角线进行计算，返回一个全局的指标。
                                                    此时要求 axis=None
            b_abs:          <boolean> 是否对矩阵先进行绝对值操作，再进行计算
    """
    matrix = np.asarray(matrix)
    if b_abs:
        matrix = np.abs(matrix)
    diag_ = np.diag(matrix)
    if reduction == "all":
        assert axis is None
        diag_sum = np.sum(diag_)
        rho = diag_sum / (np.sum(matrix) - diag_sum)
    else:
        diag_ = diag_ if axis == 0 else diag_.reshape(-1, 1)
        offdiag_sum = np.sum(matrix, axis=axis, keepdims=True) - diag_
        rho = diag_ / (offdiag_sum + eps)
        if reduction == 'mean':
            rho = np.mean(rho)
        elif reduction == 'min':
            rho = np.min(rho)
    return rho


if __name__ == "__main__":
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print(diagonal_dominance_ratio(A, axis=1))
    print(diagonal_dominance_ratio(A, axis=None, reduction='all'))
