import os
from collections import defaultdict
from tqdm import tqdm
import numpy as np
import torch
import cv2
from kevin_dl.tools.face.utils import rotate_image
from kevin_toolbox.data_flow.file import json_, kevin_notation
import kevin_toolbox.nested_dict_list as ndl
from kevin_dl.tools.variable import TOOLS


def generate_face_dataset_from_image_dataset(**kwargs):
    """
        检测并处理已有数据集图片中的人脸，并构造新的关于人脸的数据集

        检测相关参数：
            detector_settings:              <dict> 人脸检测的相关设置
            b_do_rotate_before_detect:      <boolean> 在进行人脸检测前，是否先按照其中主导人脸（分数最高的）对图片进行旋转。
                                                默认为 False
                                                若图片中存在人头倾斜颠倒的情况，尤其是在使用 MTCNN_Detector 作为检测器时，建议启用该项
            detect_results_file:            <path> 保存有对应图片检测结果的 ndl 文件
                                                其格式应该为： {<image_path>: {"detect_res_ls": [{...}, ...],
                                                                            "rotate_angle": <float or None>}, ...}
                                                            当"rotate_angle"的值非 None 时表示该 detect_res_ls 系图片旋转该角度后得到的结果
                注意：以上两组参数（detector_settings+b_do_rotate_before_detect 和 detect_results_file）二选一，
                    同时指定时，以后者为准。

        人脸转正/对齐相关参数：
            detector_settings:              <dict> 人脸转正的相关设置

        其他参数：
            dataset_file:           <path> 数据集文件
                                        支持以下两种格式：
                                            - .kvt      要求必须要有名为 "image_path" 的列
                                            - .json     格式应为 {"image_path":[...], <key_0>:[...], ...}
            image_prefix:           <path> image_path 应该补充的前缀
            output_dir:             <path> 构建完的数据集将输出该文件夹中
            b_keep_best_only:       <boolean> 是否仅为每张图片保留分数最大的一个人脸
                                        默认为 True
            b_drop_if_no_face_detected:     <boolean> 图片中检测不到人脸时，是否保留该图片
                                        默认为 True
                                        当设置为 False 时，当检测不到人脸，将会复制原图

        在 output_dir 下生成的目录结构：
            - aligned_images/   # 人脸图片
            - data_s.json       # 数据集文件，包括人脸图片的路径，原图中的其他标签、该人脸的bbox、score等
            - (data_s.kvt)      # kvt 格式的数据集文件，仅在指定的 dataset_file 为 .kvt 文件时会产生
            - detect_results.tar  # 人脸检测的结果。
            - record_for_generate_dataset.json  # 记录调用本函数时的相关参数
    """
    # 默认参数
    paras = {
        # 检测相关参数
        "detector_settings": {"name": ":face:detect:SFD_Detector", "paras": {"b_use_gpu": False}},
        "b_do_rotate_before_detect": False,
        "detect_results_file": None,
        # 人脸转正/对齐相关参数
        "alignment_settings": None,
        # 输入输出
        "dataset_file": None,
        "image_prefix": "/",
        "output_dir": None,
        #
        "b_keep_best_only": True,
        "b_drop_if_no_face_detected": True
    }

    # 获取参数
    paras.update(kwargs)

    # 校验参数
    assert not paras["image_prefix"] or os.path.isdir(paras["image_prefix"])
    os.makedirs(paras["output_dir"], exist_ok=True)
    #
    metadata = None
    if paras["dataset_file"].endswith(".json"):
        data_s = json_.read(file_path=paras["dataset_file"], b_use_suggested_converter=True)
    elif paras["dataset_file"].endswith(".kvt"):
        metadata, data_s = kevin_notation.read(file_path=paras["dataset_file"])
    else:
        raise NotImplementedError(f'dataset_file must be json or kvt file')
    #
    assert paras["detect_results_file"] is None or os.path.isfile(paras["detect_results_file"])

    #
    if paras["detect_results_file"] is not None:
        detect_results = ndl.serializer.read(input_path=paras["detect_results_file"])
        assert set(detect_results.keys()).issuperset(set(data_s["image_path"]))
        detector = None
    else:
        detector = TOOLS.get(name=paras["detector_settings"]["name"])(**paras["detector_settings"]["paras"])
        detect_results = dict()
    alignment_func = TOOLS.get(name=paras["alignment_settings"]["name"])

    out_s = defaultdict(list)
    for image_idx, image_path in enumerate(tqdm(data_s["image_path"])):
        image = cv2.cvtColor(cv2.imread(os.path.join(paras["image_prefix"], image_path)), cv2.COLOR_BGR2RGB)
        # 检测
        rotate_angle = None
        if image_path in detect_results:
            rotate_angle = detect_results[image_path].get("rotate_angle", None)
        elif paras["b_do_rotate_before_detect"]:
            rotate_angle = detector.find_best_rotate_angle(image=image)
        if rotate_angle is not None:
            image = rotate_image(
                image=image, angle=rotate_angle, b_return_rotate_matrix=False,
                **{k: v for k, v in paras["alignment_settings"]["paras"].items() if
                   k in ("border_mode", "border_value")}
            )
        #
        if image_path in detect_results:
            detect_res_ls = detect_results[image_path]["detect_res_ls"]
        else:
            detect_res_ls = detector.detect_face(image=image)
        detect_results[image_path] = {"detect_res_ls": detect_res_ls, "rotate_angle": rotate_angle}
        # 转正 & 保存图片
        if len(detect_res_ls) == 0:
            if paras["b_drop_if_no_face_detected"]:
                continue
            else:
                out_path = f'{image_path}_raw.png'
                out_file = os.path.join(paras["output_dir"], "aligned_images", out_path)
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                cv2.imwrite(filename=out_file, img=cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                #
                out_s["image_path"].append(out_path)
                for k, v in data_s.items():
                    if k != "image_path":
                        out_s[k].append(v[image_idx])
                out_s["score"].append(None)
                out_s["bbox"].append(None)
        else:
            for face_idx, it in enumerate(detect_res_ls[:1] if paras["b_keep_best_only"] else detect_res_ls):
                warped_image = alignment_func(image=image, landmarks=it["landmarks"],
                                              **paras["alignment_settings"]["paras"])
                #
                out_path = f'{image_path}_{face_idx}.png'
                out_file = os.path.join(paras["output_dir"], "aligned_images", out_path)
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                cv2.imwrite(filename=out_file, img=cv2.cvtColor(warped_image, cv2.COLOR_RGB2BGR))
                #
                out_s["image_path"].append(out_path)
                for k, v in data_s.items():
                    if k != "image_path":
                        out_s[k].append(v[image_idx])
                out_s["score"].append(it.get("score", None))
                temp = it.get("bbox", None)
                out_s["bbox"].append(temp.tolist() if isinstance(temp, np.ndarray) else temp)
                out_s["face_idx"].append(face_idx)

    # 保存新的数据集
    #   json 格式
    json_.write(file_path=os.path.join(paras["output_dir"], 'data_s.json'), content=out_s,
                b_use_suggested_converter=True)
    #   kvt 格式
    if paras["dataset_file"].endswith(".kvt"):
        metadata['column_name'].extend(['face_idx', 'score', 'bbox'])
        metadata['column_type'].extend(['int', 'float', 'list'])
        kevin_notation.write(metadata=metadata, content=out_s,
                             file_path=os.path.join(paras["output_dir"], 'data_s.kvt'))

    # 保存中间处理结果
    ndl.serializer.write(output_dir=os.path.join(paras["output_dir"], "detect_results"), var=detect_results,
                         b_pack_into_tar=True)

    # 保存生成数据集相关设置
    json_.write(file_path=os.path.join(paras["output_dir"], 'record_for_generate_dataset.json'), content=paras,
                b_use_suggested_converter=True)
