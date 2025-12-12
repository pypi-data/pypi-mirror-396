import numpy as np


def diagonal_energy_ratio(A, eps=1e-12):
    """
        计算 对角能量比例（Diagonal Energy Ratio）

        公式：
            eta_i = a_ii^2 / sum_j (a_ij^2)

        参数：

    """
    A = np.asarray(A)
    diag_sq = np.diag(A) ** 2
    row_sq_sum = np.sum(A ** 2, axis=1)
    eta = diag_sq / (row_sq_sum + eps)
    return eta
