import warnings
import numpy as np
from kevin_dl.tools.face.alignment.utils import warp_affine_and_crop_by_point_pairs
from kevin_dl.tools.variable import TOOLS
from enum import Enum


@TOOLS.register(name=":face:alignment:by_bbox:affine_trans_Match_Pattern")
class Match_Pattern(Enum):
    RAW_BBOX = "raw_bbox"
    EXPANDED_BBOX = "expanded_bbox"


DEFAULT_TEMPLATE_s = {
    "edge_corner": {
        # [(x_min,y_min),(x_min,y_max),(x_max,y_min),(x_max,y_max)]
        "key_points": np.array(
            [[0, 0], [0, 100], [100, 0], [100, 100]],
            dtype=np.float32
        ),
        "face_size": 100
    },
    "vggface2": {
        # [(x_min,y_min),(x_min,y_max),(x_max,y_min),(x_max,y_max)]
        "key_points": np.array(
            [[15, 15], [15, 115], [115, 15], [115, 115]],
            dtype=np.float32
        ),
        "face_size": 130
    }
}


@TOOLS.register(name=":face:alignment:by_bbox:affine_trans")
def affine_trans(image, template, bbox, desired_face_size=None, desired_image_size=None, padding_ls=None,
                 match_pattern="expanded_bbox", **kwargs):
    """
        基于关键点进行仿射变换的人脸转正
        根据关键点对人脸进行转正，并按照指定的人脸位置和画幅大小进行裁切

        参数：
            image:              <np.array> [n, m, 3] 原图
            bbox:               <np.ndarray/list/tuple> 人脸框，要求系 [x_min, y_min, x_max, y_max] 的形式
                                    5个关键点依次为：两个眼睛中心（先左后右）、鼻尖和两个嘴角（先左后右）
            face_size:          <int> 截取的图片中，人脸区域的大小
                                    默认为 112，也就是人脸将会占据 112X112 的方形区域
            padding_ls:         <list of int/int> [x_min, y_min, x_max, y_max] 以人脸为中心，两边多or少截取多少 margin
                                    支持负数元素，比如，设定 padding_ls=[-10, 5, 0, 0] 和 face_size=112 表示
                                        在人脸基础上往上少截取10个pixels，往左多截取5个pixels，最后所得图片大小为 102x117
            desired_size:      <list of int/int> [x_size, y_size]
                                    表示以人脸为中心，希望最终得到的图片大小。
                注意，padding_ls 和 desired_size 只需要指定一个即可，同时指定时以前者为准
        返回：
            crop_image:         <np.array> [u, v, 3]
    """
    # 检查参数
    if isinstance(template, str):
        # 使用默认模板
        assert template in DEFAULT_TEMPLATE_s, \
            f'template {template} is not supported yet.'
        template = DEFAULT_TEMPLATE_s[template]
    if isinstance(template, (dict,)):
        template = [template]
    template_ls = []
    for it in template:
        assert "key_points" in it and "face_size" in it
        template_ls.append(np.asarray(it["key_points"]) * np.asarray(desired_face_size) / np.asarray(it["face_size"]))
    assert len(template_ls) >= 1
    #
    x_min, y_min, x_max, y_max = np.asarray(bbox).reshape(4)
    assert x_min < x_max and y_min < y_max

    if Match_Pattern(match_pattern) is Match_Pattern.EXPANDED_BBOX:
        rect = max(y_max - y_min, x_max - x_min)
        x_min -= (rect - (x_max - x_min)) // 2
        x_max = x_min + rect
        y_min -= (rect - (y_max - y_min)) // 2
        y_max = y_min + rect
    src_points = np.asarray([(x_min, y_min), (x_min, y_max), (x_max, y_min), (x_max, y_max)]).reshape(4, 2)
    #
    warped = warp_affine_and_crop_by_point_pairs(
        image=image, src_points=src_points, dst_points=template_ls,
        crop_ls=None, center_size=desired_face_size, padding_ls=padding_ls, desired_size=desired_image_size,
        **kwargs
    )
    return warped


if __name__ == '__main__':
    import os
    import cv2
    from kevin_toolbox.data_flow.file import json_
    from kevin_dl.tools.face.utils import plot_bbox_and_landmarks
    from kevin_dl.tools.face.detect import MTCNN_Detector

    data_dir = "~/Desktop/gitlab_repos/kevin_dl/kevin_dl/tools/face/test/test_data"
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    detector = MTCNN_Detector()
    for image_path in ["head_pose/pitch/30.png", "head_pose/yaw/30.png", "head_pose/yaw/90.png",
                       "head_pose/raw_face/0.png"]:
        ori_image = cv2.cvtColor(cv2.imread(os.path.join(data_dir, image_path)), cv2.COLOR_BGR2RGB)
        res = detector.detect_face(image=ori_image)[0]
        ann_image = plot_bbox_and_landmarks(image=ori_image, landmarks=res["landmarks"], bbox=res["bbox"],
                                            b_inplace=False)
        #
        # warped_image = affine_trans(image=ann_image, bbox=res["bbox"], template="vggface2",mode="expanded_bbox", desired_face_size=140)
        # warped_image = affine_trans(image=ann_image, bbox=res["bbox"], template="edge_corner", mode="expanded_bbox",
        #                             desired_face_size=108, padding_ls=0.15)
        warped_image = affine_trans(image=ann_image, bbox=res["bbox"], template="edge_corner", mode="expanded_bbox",
                                    desired_face_size=108, desired_image_size=1.3)
        cv2.imwrite(os.path.join(output_dir, image_path.replace("/", "---")),
                    cv2.cvtColor(warped_image, cv2.COLOR_RGB2BGR))
