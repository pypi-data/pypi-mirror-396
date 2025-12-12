import numpy as np


def convert_to_2_dim_array(x):
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[None, ...]
    return x


def neaten_bboxes(bboxes):
    bboxes = convert_to_2_dim_array(x=bboxes).astype(float)
    assert bboxes.ndim == 2 and bboxes.shape[1] >= 4
    return bboxes


def neaten_keypoints(keypoints):
    keypoints = convert_to_2_dim_array(x=keypoints).astype(float)
    assert keypoints.ndim == 2 and keypoints.shape[1] >= 2
    return keypoints


def neaten_crop_size(size, img_hw, b_pad_if_needed):
    if not isinstance(size, (list, tuple,)):
        size = [size, size]
    assert len(size) == 2
    res = []
    for i, j in zip(size, img_hw):
        if i is None or (i > j and not b_pad_if_needed):
            i = j
        assert i > 0
        res.append(i)
    return res


def neaten_padding(padding):
    """
        统一转换为 (left, top, right, bottom)

        参数：
            padding:            <int/tuple/list/dict> 填充边缘的大小
                                    如果提供的是单个整数，则用于填充所有边框。
                                    如果提供的是序列
                                        - 长度为 2，则分别用于填充左/右和上/下的边框。
                                        - 长度为 4，则分别用于填充左、上、右和下边框。
                                    如果提供的是字典，则需要输入形如 {"left":..., "top":..., "right":..., "bottom":...} 来指定四边的填充大小
    """
    if padding is None:
        return padding
    if isinstance(padding, dict):
        padding = [padding.get(k, 0) for k in ["left", "top", "right", "bottom"]]
    if isinstance(padding, int):
        return tuple([padding] * 4)
    if isinstance(padding, (tuple, list)):
        if len(padding) == 2:
            return tuple(list(padding) * 2)
        elif len(padding) == 4:
            return tuple(padding)
    raise ValueError(f"Unsupported padding: {padding}")
