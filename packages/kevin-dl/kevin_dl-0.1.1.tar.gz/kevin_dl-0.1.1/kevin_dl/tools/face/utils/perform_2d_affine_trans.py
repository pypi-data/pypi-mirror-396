import numpy as np


def perform_2d_affine_trans(trans_mat, points):
    """
        计算 points 经过 trans_mat 变换后的坐标
    """
    points = np.asarray(points).reshape(-1, 2)
    points = np.insert(points, 2, values=np.ones(len(points)), axis=1)
    res = np.dot(trans_mat[:2, ...], points.T).T
    return res
