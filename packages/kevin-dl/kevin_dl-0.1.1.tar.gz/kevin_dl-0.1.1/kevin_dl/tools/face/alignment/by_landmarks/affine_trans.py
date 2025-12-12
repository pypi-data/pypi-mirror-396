import warnings
import numpy as np
from kevin_dl.tools.face.utils import parse_landmarks
from kevin_dl.tools.face.alignment.utils import warp_affine_and_crop_by_point_pairs
from kevin_dl.tools.variable import TOOLS
from enum import Enum


@TOOLS.register(name=":face:alignment:by_landmarks:affine_trans_Match_Pattern")
class Match_Pattern(Enum):
    EYES_NOSE_MOUTH = "eyes_nose_mouth"
    EYE2EYE = "eye2eye"
    EYES2MOUTH = "eyes2mouth"
    EYE2EYE_OR_EYES2MOUTH = "eye2eye_or_eyes2mouth"


def _cal_eyes_to_eye_mouth_ratio(inputs):
    eyes = np.sqrt(np.sum(np.square(inputs["left_eye"] - inputs["right_eye"])))
    eye_mouth = np.sqrt(np.sum(np.square(inputs["eyes_center"] - inputs["mouth_center"])))
    return eyes / eye_mouth


DEFAULT_TEMPLATE_s = {
    # from: https://github.com/deepinsight/insightface/blob/master/recognition/arcface_mxnet/common/face_align.py
    "arcface": {
        "key_points": np.array(
            [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366], [41.5493, 92.3655], [70.7299, 92.2041]],
            dtype=np.float32
        ),
        "face_size": 112
    },
    "insightface": [
        {
            "key_points": np.array(
                [[51.642, 50.115], [57.617, 49.990], [35.740, 69.007], [51.157, 89.050], [57.025, 89.702]],
                dtype=np.float32
            ),
            "face_size": 112
        },
        {
            "key_points": np.array(
                [[45.031, 50.118], [65.568, 50.872], [39.677, 68.111], [45.177, 86.190], [64.246, 86.758]],
                dtype=np.float32
            ),  # <--left
            "face_size": 112
        },
        {
            "key_points": np.array(
                [[39.730, 51.138], [72.270, 51.138], [56.000, 68.493], [42.463, 87.010], [69.537, 87.010]],
                dtype=np.float32
            ),  # ---frontal
            "face_size": 112
        },
        {
            "key_points": np.array(
                [[46.845, 50.872], [67.382, 50.118], [72.737, 68.111], [48.167, 86.758], [67.236, 86.190]],
                dtype=np.float32
            ),  # -->right
            "face_size": 112
        },
        {
            "key_points": np.array(
                [[54.796, 49.990], [60.771, 50.115], [76.673, 69.007], [55.388, 89.702], [61.257, 89.050]],
                dtype=np.float32
            ),  # -->right profile
            "face_size": 112
        }
    ]
}
for k, v in list(DEFAULT_TEMPLATE_s.items()):
    v = v if isinstance(v, list) else [v]
    temp = []
    for it in v:
        temp.append({
            "key_points": it["key_points"] - 8,  # 把下巴也包含进来
            "face_size": it["face_size"]
        })
    DEFAULT_TEMPLATE_s[f'{k}_with_chin'] = temp


@TOOLS.register(name=":face:alignment:by_landmarks:affine_trans")
def affine_trans(image, template, landmarks, desired_face_size=None, desired_image_size=None, padding_ls=None,
                 match_pattern="eyes_nose_mouth", **kwargs):
    """
        基于关键点进行仿射变换的人脸转正
        根据关键点对人脸进行转正，并按照指定的人脸位置和画幅大小进行裁切

        参数：
            image:              <np.array> [n, m, 3] 原图
            landmarks:          <np.array> [5, 2] 关键点
                                    5个关键点依次为：两个眼睛中心（先左后右）、鼻尖和两个嘴角（先左后右）
            face_size:          <int> 截取的图片中，人脸区域的大小
                                    默认为 112，也就是人脸将会占据 112X112 的方形区域
            padding_ls:         <list of int/int> [x_min, y_min, x_max, y_max] 以人脸为中心，两边多or少截取多少 margin
                                    支持负数元素，比如，设定 padding_ls=[-10, 5, 0, 0] 和 face_size=112 表示
                                        在人脸基础上往上少截取10个pixels，往左多截取5个pixels，最后所得图片大小为 102x117
            desired_size:      <list of int/int> [x_size, y_size]
                                    表示以人脸为中心，希望最终得到的图片大小。
                注意，padding_ls 和 desired_size 只需要指定一个即可，同时指定时以前者为准

        还有 border_value 和 border_mode 等参数
        返回：
            crop_image:         <np.array> [u, v, 3]
    """
    global DEFAULT_TEMPLATE_s
    # 检查参数
    # 不同模式需要匹配不同的位置
    if Match_Pattern(match_pattern) is Match_Pattern.EYES_NOSE_MOUTH:
        # 利用双眼、鼻尖、两个嘴角的5个关键点进行仿射变换
        points_name_ls = ("left_eye", "right_eye", "nose_tip", "left_mouth_corner", "right_mouth_corner")
    elif Match_Pattern(match_pattern) is Match_Pattern.EYE2EYE:
        # 双眼
        points_name_ls = ("left_eye", "right_eye")
    elif Match_Pattern(match_pattern) is Match_Pattern.EYES2MOUTH:
        # 双眼中心和嘴巴中心
        #   "left_eye", "right_eye" ==> "eyes_center"
        #   "left_mouth_corner", "right_mouth_corner" ==> "mouth_center"
        points_name_ls = ("eyes_center", "mouth_center")
    elif Match_Pattern(match_pattern) is Match_Pattern.EYE2EYE_OR_EYES2MOUTH:
        # 在 EYE2EYE 和 EYES2MOUTH 两种模式之间切换
        points_name_ls = ("left_eye", "right_eye", "eyes_center", "mouth_center")
    else:
        raise NotImplementedError(f'{match_pattern} is not supported yet.')
    #
    landmarks = parse_landmarks(landmarks=landmarks, output_contents=points_name_ls, output_format="dict")
    #
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
        k_pts = parse_landmarks(landmarks=it["key_points"], output_contents=points_name_ls, output_format="dict")
        template_ls.append({k: v * np.asarray(desired_face_size) / np.asarray(it["face_size"]) for k, v in
                            k_pts.items()})
    assert len(template_ls) >= 1

    #
    if Match_Pattern(match_pattern) in [Match_Pattern.EYE2EYE, Match_Pattern.EYES2MOUTH,
                                        Match_Pattern.EYE2EYE_OR_EYES2MOUTH] and len(template) > 1:
        # 模板数量大于1。
        #   对于模式A，由于只有两个匹配点，因此无法比较不同模板之间的匹配误差，因此将选择第一个模板。
        warnings.warn(
            f'number of template is {len(template_ls)}, greater than 1.\n\t'
            f'For match_pattern {match_pattern}, since there are only two matching points, '
            f'the matching errors between different templates cannot be compared, '
            f'so the first template will be selected.',
            UserWarning
        )
        template_ls = template_ls[:1]
    #
    if Match_Pattern(match_pattern) is Match_Pattern.EYE2EYE_OR_EYES2MOUTH:
        if _cal_eyes_to_eye_mouth_ratio(landmarks) > _cal_eyes_to_eye_mouth_ratio(template_ls[0]):
            # 眼距大于模板，选择 EYE2EYE
            points_name_ls = ("left_eye", "right_eye")
        else:
            points_name_ls = ("eyes_center", "mouth_center")

    warped = warp_affine_and_crop_by_point_pairs(
        image=image,
        src_points=parse_landmarks(landmarks=landmarks, output_contents=points_name_ls, output_format="array"),
        dst_points=[parse_landmarks(landmarks=it, output_contents=points_name_ls, output_format="array")
                    for it in template_ls],
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
        warped_image = affine_trans(image=ann_image, template="insightface", landmarks=res["landmarks"],
                                    desired_face_size=224, desired_image_size=224,
                                    match_pattern="eyes_nose_mouth", border_value=0.0)
        cv2.imwrite(os.path.join(output_dir, image_path.replace("/", "-")),
                    cv2.cvtColor(warped_image, cv2.COLOR_RGB2BGR))
