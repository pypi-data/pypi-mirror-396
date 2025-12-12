import cv2
import numpy as np
from kevin_dl.tools.face.utils import cal_2d_affine_trans_matrix


def warp_affine_and_crop_by_point_pairs(image, src_points, dst_points, crop_ls=None, center_size=None,
                                        padding_ls=None, desired_size=None, border_mode=cv2.BORDER_CONSTANT,
                                        border_value=0.0, **kwargs):
    """
        根据点对 src 和 dst 计算变换矩阵对图片进行仿射变换，然后进行裁剪
            大部分人脸转正函数都是基于本函数进行实现

        仿射变换相关参数：
            image:              <np.array> [n, m, c] 原始图像
            src_points:         <np.array or list of np.array> 原始图像中的点
                                    当 src_points 为 list of np.array 时，表示其中有多个模板用于匹配。将会尝试使用其中所有模板与 dst_points
                                        计算仿射变换矩阵，然后选取其中拟合程度最佳（经过变换后的 src_points 与 dst_points 的距离最为接近的）的模板。
            dst_points:         <np.array or list of np.array> 目标图像中的点
                                    同样支持多个模板
        裁剪范围相关参数：
            crop_ls:            <list of int/float> [x_min, y_min, x_max, y_max] 仿射变换后，要裁剪的图像区域
                                    当元素为 float 时，表示该值为相对于 image.shape 的相对值。
            center_size:        <list of int or float/int or float> [x_size, y_size] 裁剪的中心区域
                                    当元素为 float 时，表示该值为相对于 image.shape 的相对值。
            padding_ls:         <list of int or float/int or float> [x_min, y_min, x_max, y_max] 以 center_size 部分为中心，两边多or少截取多少 margin
                                    支持负数元素，比如 padding_ls = [-10, 5, 0, 0]
                                    支持float元素，表示相对于 center_size 的相对值。
            desired_size:      <list of int or float/int or float> [x_size, y_size]
                                    表示以 center_size 为中心，希望最终得到的图片大小。
                                    支持float元素，表示相对于 center_size 的相对值。
                有三种指定裁剪范围的方式：
                    1. 直接用 crop_ls
                    2. center_size + padding_ls
                        等效于 crop_ls = [-padding_ls[0], -padding_ls[1],
                                        center_size[0]+padding_ls[2], center_size[1]+padding_ls[3]]
                    3. center_size + desired_size
                        等效于 padding_ls = [(desired_size[0]-center_size[0])//2, ...] 时计算出来的 crop_ls
                以上几种指定方式同时指定时，采用的优先级由上到下
            border_value:        <int/float or tuple of int/float> 对于边缘空白区域填充什么值

        返回：
            crop_image:         <np.array> [u, v, c]
    """
    global T_FORM
    # 检验参数
    if crop_ls is None:
        center_size = _deal_size_paras(inputs=center_size, refers=image.shape[:2], target_shape=[2])
        if padding_ls is None:
            desired_size = _deal_size_paras(inputs=desired_size, refers=center_size, target_shape=[2])
            # 将 desired_size 统一转为 padding_ls
            padding_ls = [(i - j) // 2 for i, j in zip(desired_size, center_size)]
            padding_ls += [j - k - i for i, j, k in zip(padding_ls, desired_size, center_size)]
        else:
            padding_ls = _deal_size_paras(inputs=padding_ls, refers=center_size.tolist() + center_size.tolist(),
                                          target_shape=[4])
        # 统一转换为 crop_ls
        crop_ls = [-padding_ls[0], -padding_ls[1],
                   center_size[0] + padding_ls[2], center_size[1] + padding_ls[3]]
    crop_ls = np.asarray(crop_ls)
    assert crop_ls.shape == (4,) and np.all((crop_ls[-2:] - crop_ls[:2]) > 0)
    #
    src_points = np.asarray(src_points)
    dst_points = np.asarray(dst_points)
    if src_points.ndim == 2:
        src_points = src_points[None, ...]
    if dst_points.ndim == 2:
        dst_points = dst_points[None, ...]
    assert len(src_points) > 0 and len(dst_points) > 0 and src_points.ndim == dst_points.ndim == 3
    assert src_points.shape[2] == dst_points.shape[2] == 2 and src_points.shape[1] == dst_points.shape[1] > 1
    #
    dst_points = dst_points - crop_ls[:2][None, None, ...]

    # 变换矩阵
    best_error, best_trans_mat = float("inf"), None
    for src in src_points:
        for dst in dst_points:
            trans_mat, error_ls = cal_2d_affine_trans_matrix(src=src, dst=dst, b_compact_form=True, b_return_error=True)
            error = np.sum(error_ls)
            if error < best_error:
                best_error, best_trans_mat = error, trans_mat
    warped = cv2.warpAffine(image, best_trans_mat, (crop_ls[-2:] - crop_ls[:2]), borderMode=border_mode,
                            borderValue=border_value)

    return warped


def _deal_size_paras(inputs, refers, target_shape):
    """
        处理 size 类型参数

        参数：
            inputs:             原始参数值。
            refers:             参考值，当原始值为 None 时返回该值。
            target_shape:       当设置有时，若待返回的值的形状不满足，则尝试将待返回值 reshape 成该形状。
    """
    if refers is not None:
        refers = np.asarray(refers)
        if target_shape is not None and refers.shape != target_shape:
            if refers.size == 1:
                refers = np.repeat(refers, np.prod(target_shape))
            refers = refers.reshape(target_shape)
        assert issubclass(refers.dtype.type, np.integer)
    #
    if inputs is None:
        assert refers is not None
        inputs = refers
    else:
        inputs = np.asarray(inputs)
        if target_shape is not None and inputs.shape != target_shape:
            if inputs.size == 1:
                inputs = np.repeat(inputs, np.prod(target_shape))
            inputs = inputs.reshape(target_shape)
        # 如果是小数，则参考 refers，转换成整数。
        if issubclass(inputs.dtype.type, np.inexact):
            assert refers is not None
            inputs = np.round(inputs * refers).astype(int)

    return inputs


if __name__ == '__main__':
    import os
    from kevin_toolbox.data_flow.file import json_
    from kevin_dl.tools.face.utils import plot_bbox_and_landmarks

    data_dir = "~/Desktop/gitlab_repos/kevin_dl/kevin_dl/tools/face/test/test_data"

    # 这个基准是112*96的面部特征点的坐标
    BASIC_LANDMARK = np.array([
        [30.2946, 51.6963],
        [65.5318, 51.5014],
        [48.0252, 71.7366],
        [33.5493, 92.3655],
        [62.7299, 92.2041]], dtype=np.float32)  # 5个关键点依次为：两个眼睛中心（先左后右）、鼻尖和两个嘴角（先左后右）
    BASIC_LANDMARK[:, 0] += 8  # 转为112*112的坐标
    BASIC_LANDMARK[:, 1] -= 8  # 把下巴也包含进来

    # 读取关键点
    ann_s = json_.read(file_path=os.path.join(data_dir, "ann_s_for_Tadokor_Koji_the_Japanese_representative.json"),
                       b_use_suggested_converter=True)
    landmarks = ann_s["detect_faces"][0]["landmarks"]

    # 读取图片
    image = cv2.imread(os.path.join(data_dir, ann_s["image_path"]))

    crop_image = warp_affine_and_crop_by_point_pairs(image=image, src_points=landmarks, dst_points=BASIC_LANDMARK,
                                                     center_size=112, padding_ls=[-8, 0, -8, 0])
    BASIC_LANDMARK[:, 0] -= 8
    print(BASIC_LANDMARK)
    plot_bbox_and_landmarks(image=crop_image, landmarks=BASIC_LANDMARK, b_inplace=True)
    cv2.imwrite(os.path.join(data_dir, "crop_image3.jpg"), crop_image)
    # 在 cv2 读取的图片中，各个维度和坐标轴的对应关系是 [y(高), x(宽), c(通道数)]
    assert crop_image.shape == (112, 96, 3)

    cv2.imwrite(os.path.join(data_dir, "crop_image4.jpg"), np.ones([112, 10, 3]) * 255)
