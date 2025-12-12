import cv2
import numpy as np
from skimage import transform
from kevin_dl.tools.face.utils.perform_2d_affine_trans import perform_2d_affine_trans

tform = transform.SimilarityTransform()


def cal_2d_affine_trans_matrix(src, dst, b_compact_form=True, b_return_error=False):
    """
        计算一个仿射变换矩阵，使点集 src 变换到接近 dst 对应的位置

        参数：
            src：                <np.ndarray> [n, 2]
            dst：                <np.ndarray> [n, 2]
            b_compact_form:     <boolean> 是否输出变换矩阵的紧凑形式
                                    仿射变换矩阵最后一行为 (0,0,1) 因此可以省略。
                                    默认为 True，此时省略最后一行，输出紧凑形式。
            b_return_error:     <boolean> 是否返回经过变换后的src与dst的误差（平均距离）
                                    默认为 False
        返回：
            trans_mat:          <np.ndarray> [2, 3]or[3, 3] 仿射变换矩阵
            error_ls:              <float> 误差（平均距离）
    """
    global tform
    # 检验参数
    src = np.asarray(src).reshape(-1, 2)
    dst = np.asarray(dst).reshape(-1, 2)
    assert src.shape == dst.shape and src.shape[0] > 1
    #
    tform.estimate(src=src, dst=dst)
    trans_mat = tform.params
    if b_compact_form:
        trans_mat = trans_mat[0:2, :]

    if b_return_error:
        error_ls = np.sqrt(np.sum((dst - perform_2d_affine_trans(trans_mat=trans_mat, points=src)) ** 2, axis=1))
        return trans_mat, error_ls
    else:
        return trans_mat
