import numpy as np


def crop_bboxes(bboxes, img_hw):
    h_, w_ = img_hw
    bboxes[:, 0] = np.maximum(bboxes[:, 0], 0)
    bboxes[:, 1] = np.maximum(bboxes[:, 1], 0)
    bboxes[:, 2] = np.minimum(bboxes[:, 2], w_)
    bboxes[:, 3] = np.minimum(bboxes[:, 3], h_)
    # 被完全裁剪掉的 bbox，则将其移除
    temp = (bboxes[:, 0] < bboxes[:, 2]) * (
            bboxes[:, 1] < bboxes[:, 3])
    bboxes = bboxes[temp]
    return bboxes
