import os
import torch
from kevin_dl.deploy import run_onnx_model
from kevin_dl.models.api.utils import parse_preprocess, parse_postprocess, parse_model_name, fix_image_channel_order
import onnxruntime as ort

ort.set_default_logger_severity(3)


def run_model(input_s, model_name=None, b_use_gpu=torch.cuda.is_available()):
    """
        模型推理。

        参数：
            input_s:        <dict> 输入
                                需要包含以下键值对：
                                    - image:            <np.array> 图像
                                可选以下键值对：
                                    - b_bgr_image:      <boolean> 是否是 bgr 图像
                                                            不指定时，默认为 False
            model_name:     <str> 模型的名称或者路径。
                                目前支持直接通过以下名称调用内置模型：
                                    - 单目活体判断：
                                        - "onnx/liveness/10-4-58"
                                        - "onnx/liveness/10-1-198"
                                        - ...
                                    - 图片旋转角度预测：
                                        - "onnx/image_rotate/0-1-3"
                                    - 人脸属性预测（低频变化属性，年龄、性别、人种）
                                        - "onnx/face_attr/3-2-6"
                                    - 人脸属性预测（高频变化属性，睁闭眼、表情）
                                        - "onnx/face_attr/2-50-3"
                                当输入的系路径时，该路径下需要包括以下文件：
                                    - preprocess.json       指定数据的前处理和模型输入的前处理等，使用 parse_preprocess() 进行解释
                                    - postprocess.json      指定模型的输出后处理，使用 parse_postprocess() 进行解释
                                    - model.onnx            模型
                                    - inputs_mapper.py（可选）      包含 inputs_mapper()，用于指定模型输入的前处理的具体方式
                                    - outputs_mapper.py（可选）     包含 outputs_mapper()，用于指定模型的输出的后处理的具体方式
    """
    if model_name is None or input_s["image"] is None:
        return input_s

    temp = parse_model_name(model_name)
    model_name, model_path = temp["model_name"], temp["model_path"]

    pre_s = parse_preprocess(model_name=model_name, model_path=model_path)
    post_s = parse_postprocess(model_name=model_name, model_path=model_path)

    # load image
    image = fix_image_channel_order(image=input_s["image"], b_bgr_raw=input_s.get("b_bgr_image", False),
                                    b_bgr_dst=pre_s["b_bgr_image"])
    input_s.update(image=image, b_bgr_image=pre_s["b_bgr_image"])

    # preprocess
    out_s = pre_s["pipeline"]({"image": image})
    inputs = pre_s["inputs_mapper"](out_s)

    # run model
    res = run_onnx_model(model_path=os.path.join(model_path, "model.onnx"), inputs=inputs, b_use_gpu=b_use_gpu)

    # postprocess
    res_s = post_s["outputs_mapper"](res)
    input_s.setdefault("results_ls", list())
    input_s.setdefault("details_ls", list())
    input_s["results_ls"].append(res_s)
    input_s["details_ls"].append(dict(operator_name="run_model", paras=dict(model_name=model_name)))

    return input_s


if __name__ == "__main__":
    from kevin_dl.utils.variable import root_dir

    image = os.path.join(root_dir, "kevin_dl/models/test/test_data/data_1/0.bmp")
    input_s = dict(image=image)
    # 图片旋转角度预测
    input_s = run_model(
        input_s=input_s,
        model_name="onnx/image_rotate/0-1-3"
    )
    print(input_s["results_ls"][-1])

    # 单目活体判断
    input_s = run_model(
        input_s=input_s,
        model_name="onnx/liveness/10-4-81"
    )
    print(input_s["results_ls"][-1])

    # 人脸属性预测（低频变化属性，年龄、性别、人种）
    input_s = run_model(
        input_s=input_s, model_name="onnx/face_attr/3-2-6"
    )
    print(input_s["results_ls"][-1])
    # from kevin_toolbox.data_flow.file import json_
    # import kevin_toolbox.nested_dict_list as ndl
    # import numpy as np
    #
    # res = ndl.traverse(var=input_s["results_ls"][-1],
    #                    match_cond=lambda _, __, v: not isinstance(v, (list, dict)),
    #                    action_mode="replace",
    #                    converter=lambda _, v: v.tolist() if isinstance(v, np.ndarray) else (
    #                        v if isinstance(v, (str, type(None))) else float(v)))
    #
    # json_.write(content=res, file_path=None, b_use_suggested_converter=True)
    # breakpoint()

    # image = "~/Desktop/gitlab_repos/face_liveness/face_liveness/for_sdk/align_with_sdk/2025-06-13_from_benjie/out_affineTransformImage_178x218x3.png"
    # input_s = dict(image=image)
    #
    # from kevin_toolbox.data_flow.file import markdown
    #
    # # 人脸属性预测（高频变化属性，睁闭眼、表情）
    # input_s = run_model(
    #     input_s=input_s, model_name="onnx/face_attr/2-50-3"
    # )
    # print(markdown.generate_list(
    #     var={k: v for k, v in input_s["results_ls"][-1].items() if k in ["Eye", "Glass", "Sunglass"]}))
