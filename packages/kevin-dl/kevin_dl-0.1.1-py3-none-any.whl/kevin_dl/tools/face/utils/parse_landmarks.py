import numpy as np
from enum import Enum


class Output_Format(Enum):
    DICT = "dict"
    ARRAY = "array"


def parse_landmarks(landmarks, output_contents=None, output_format=Output_Format.DICT):
    """
        将关键点序列解释为各个部位的坐标

        参数：
            landmarks:          <np.ndarray/dict> 关键点
                                对于 np.ndarray，支持以下形式的输入:
                                    - 5个2d关键点。
                                        依次为：
                                            0-1：两个眼睛中心（先左后右）
                                            2：鼻尖
                                            3-4：两个嘴角（先左后右）
                                    - 68个2d关键点。
                                    - 106个2d关键点。
                                对于 dict，支持以下形式的输入:
                                    - <dict> 按照 {<部位名称>: <np.ndarray>, ...} 的形式组织
            output_contents:    <list of str> 要解释出哪些部位的坐标
                                目前支持以下部位：
                                    - left_eye, right_eye
                                    - eyes_center
                                    - left_mouth_corner, right_mouth_corner
                                    - mouth_center（对于5关键点，该中心点系left_mouth_corner和right_mouth_corner的均值）
                                    - nose_tip
                                    - rightmost, leftmost, topmost, bottommost （最边缘的关键点）
                                当设置为 None 时，返回所有部位的坐标
                                默认为 None。
            output_format:      <str> 输出的格式
                                目前支持两种输出格式：
                                    - "dict":       <dict> 按照 {<部位名称>: <np.ndarray>, ...} 的形式组织
                                    - "array":      <np.ndarray> 按照 output_contents 中部位名称的顺序concat成一个array
                                        当 output_contents 为空时，不支持该种格式的输出
    """
    assert isinstance(output_contents, (list, tuple, type(None)))

    #
    if isinstance(landmarks, dict):
        res_s = landmarks
    else:
        landmarks = np.asarray(landmarks).reshape(-1, 2)
        sorted_by_x = sorted(list(landmarks), key=lambda x: x[0])
        sorted_by_y = sorted(list(landmarks), key=lambda x: x[1])
        if len(landmarks) == 5:
            # 5个关键点依次为：两个眼睛中心（先左后右）、鼻尖和两个嘴角（先左后右）
            res_s = {
                'left_eye': landmarks[0],
                'right_eye': landmarks[1],
                'nose_tip': landmarks[2],
                'left_mouth_corner': landmarks[3],
                'right_mouth_corner': landmarks[4]
            }
        elif len(landmarks) == 68:
            # 68个关键点
            res_s = {
                'left_eye': (landmarks[36] + landmarks[39]) / 2,
                'right_eye': (landmarks[42] + landmarks[45]) / 2,
                'nose_tip': landmarks[30],
                'left_mouth_corner': landmarks[48],
                'right_mouth_corner': landmarks[54]
            }
        elif len(landmarks) == 106:
            # 106个关键点
            res_s = {
                'left_eye': landmarks[104],
                'right_eye': landmarks[105],
                'nose_tip': landmarks[46],
                'left_mouth_corner': landmarks[84],
                'right_mouth_corner': landmarks[90]
            }
        else:
            raise ValueError(
                f'Currently only supports 5, 68, 106 landmarks, but got {len(landmarks)} key points.')
        res_s.update({
            'leftmost': sorted_by_x[0],
            'topmost': sorted_by_y[0],
            'rightmost': sorted_by_x[-1],
            'bottommost': sorted_by_y[-1]
        })
    if (output_contents is None or "mouth_center" in output_contents) and "mouth_center" not in res_s:
        res_s["mouth_center"] = (res_s["left_mouth_corner"] + res_s["right_mouth_corner"]) / 2
    if (output_contents is None or "eyes_center" in output_contents) and "eyes_center" not in res_s:
        res_s["eyes_center"] = (res_s["left_eye"] + res_s["right_eye"]) / 2

    #
    if Output_Format(output_format) is Output_Format.ARRAY:
        assert output_format is not None, \
            f'output_format must be specified when output_format is "array".'
        res = np.concatenate([res_s[k][None, ...] for k in output_contents], axis=0)
    elif Output_Format(output_format) is Output_Format.DICT:
        res = {k: v for k, v in res_s.items() if k in output_contents} if output_contents is not None else res_s
    else:
        raise ValueError(f'Unsupported output_format: {output_format}.')

    return res
