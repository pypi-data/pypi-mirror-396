import os
import cv2
from collections import defaultdict
from kevin_toolbox.patches.for_os import find_files_in_dir
from kevin_toolbox.computer_science.algorithm.cache_manager import Cache_Manager
from kevin_toolbox.data_flow.file import json_
from kevin_dl.models.api.utils.variable import setting_for_kevin_sdk_s

model_s_cache = Cache_Manager(upper_bound=setting_for_kevin_sdk_s["cache_size"]["model"])

default_model_setting_s = {}
temp = os.path.expanduser("~/.kv_dl_cfg/.run_kevin_sdk_face_detect.json")
if os.path.isfile(temp):
    default_model_setting_s = json_.read(file_path=temp, b_use_suggested_converter=True)


def get_model(model_type, model_path, **kwargs):
    global model_s_cache
    try:
        from kevin_sdk.api import build_model
    except:
        raise ImportError(f'you must install kevin_sdk first')

    model_path = os.path.abspath(os.path.expanduser(model_path))

    if not model_s_cache.has(key=(model_type, model_path)):
        model_s_cache.add(
            key=(model_type, model_path),
            value=build_model(model_type=model_type, model_path=model_path, **kwargs)
        )
    model = model_s_cache.get(key=(model_type, model_path))
    return model


def run_kevin_sdk_face_detect(image_ls=None, input_dir=None, output_contents=("landmarks", "face_bbox"), **kwargs):
    """
        使用 kevin_sdk 进行推理。

        参数：
            image_ls:       <list of path/np.array> 要处理的图片列表。
                                列表元素支持通过 path 或者 np.ndarray 来指定图片。
                                默认为 None，此时若 input_dir 非空，则将从 input_dir 中找出所有 png, jpg, bmp 格式的图片。
            input_dir:      <path> 输入路径。
                                将从下面找出需要处理的图片。
                        注意，以上两个参数不能同时为空。
            output_contents:<list of str> 需要输出哪些内容。
                                目前支持：
                                    - "landmarks"       返回 106 关键点
                                    - "face_bbox"       按照 [x_min, y_min, x_max, y_max] 的格式返回。
        模型等配置项相关参数：
            detect_model_path:  <path> 检测模型
            align_model_path:   <path/list of path> face align 模型，支持多个 align 模型串联进行校准
            align_model_type:   <str> align 模型的种类
    """
    global default_model_setting_s
    assert input_dir is not None or image_ls is not None, \
        "you must set input_dir or image_ls"
    if image_ls is None:
        image_ls = find_files_in_dir(input_dir, suffix_ls=["png", "jpg", "jpeg", "bmp"], b_relative_path=True,
                                     b_ignore_case=True)
        image_ls = list(image_ls)

    try:
        from kevin_sdk.api import build_model, detect, align
        from kevin_sdk.api.utils import parse_cv_image_t
        from kevin_dl.models.api.utils.variable import setting_s
    except:
        raise ImportError(f'you must install kevin_sdk first')

    detect_model_path = kwargs.get("detect_model_path", default_model_setting_s["detect_model_path"])
    align_model_path = kwargs.get("align_model_path", default_model_setting_s["align_model_path"])
    align_model_type = kwargs.get("align_model_type", default_model_setting_s["align_model_type"])
    if not isinstance(align_model_path, (list, tuple)):
        align_model_path = [align_model_path, ]
    if not isinstance(align_model_type, (list, tuple)):
        align_model_type = [align_model_type, ]

    # build model
    handle_detect = get_model(model_type='detect', model_path=detect_model_path)
    handle_align_ls = [get_model(model_type=j, model_path=i) for i, j in zip(align_model_path, align_model_type)]

    res_ls = []
    # run model
    for image in image_ls:
        if isinstance(image, str):
            image = cv2.imread(image)
        image = parse_cv_image_t(var=image, b_reverse=True)
        detect_res_ls = detect(image=image, model=handle_detect, b_parse_result=True)
        res_s = defaultdict(dict)
        for i, detect_res_s in enumerate(detect_res_ls):
            if 'face_bbox' in output_contents:
                res_s[i]["face_bbox"] = [detect_res_s["bbox"][k] for k in ('left', 'top', 'right', 'bottom')]
                res_s[i]["detect_res"] = detect_res_s
            if 'landmarks' in output_contents:
                temp = align(image=image, model=handle_align_ls, bbox=detect_res_s["bbox"], b_parse_result=True)

                temp["points"] = list(zip(temp["points"]["x"], temp["points"]["y"]))
                res_s[i]["landmarks"] = temp
        res_ls.append(res_s)

    return res_ls


if __name__ == '__main__':
    from kevin_dl.utils.variable import root_dir
    from kevin_dl.tools.face.utils import plot_bbox_and_landmarks

    image_ls_ = [
        os.path.join(root_dir, "kevin_dl/models/api/utils/for_sdk_detect/test/test_data/images/face_02.jpg"),
        os.path.join(root_dir, "kevin_dl/models/api/utils/for_sdk_detect/test/test_data/images/test2.png"),
        os.path.join(root_dir, "kevin_dl/models/api/utils/for_sdk_detect/test/test_data/images_1/face_05.jpg")
    ]

    res_ls_ = run_kevin_sdk_face_detect(
        input_dir=os.path.join(root_dir, "kevin_dl/models/api/utils/for_sdk_detect/test/test_data/images"),
        image_ls=image_ls_[:2] + [cv2.imread(image_ls_[-1])]
        , output_contents=("landmarks", "face_bbox"))
    print(res_ls_)

    for i, image_ in enumerate(image_ls_):
        image_ls_[i] = cv2.imread(image_)

    output_dir = os.path.join(root_dir, "kevin_dl/models/test/temp")
    os.makedirs(output_dir, exist_ok=True)
    for i, (image_, res_s_) in enumerate(zip(image_ls_, res_ls_)):
        for k, v_s in res_s_.items():
            image_ = plot_bbox_and_landmarks(image=image_, bbox=v_s["face_bbox"], landmarks=v_s["landmarks"]["points"],
                                             person_id=k)
        cv2.imwrite(os.path.join(output_dir, f"{i}.png"), image_)
