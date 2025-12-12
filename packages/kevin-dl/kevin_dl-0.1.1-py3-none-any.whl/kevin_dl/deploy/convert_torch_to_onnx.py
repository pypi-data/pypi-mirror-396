import os
import torch
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.nested_dict_list import serializer
from kevin_toolbox.patches.for_test import check_consistency
from kevin_dl.deploy.run_onnx_model import run_onnx_model

"""
参考：从pytorch转换到onnx https://zhuanlan.zhihu.com/p/422290231
"""


def convert_torch_to_onnx(model, inputs, output_dir, b_check_consistency=True,**kwargs):
    """
        参数：
            inputs:             <tuple/tensor>
            tolerance:          <float> 检查转换前后模型输出是否一致时的容忍误差
                                    默认为 1e-5
            dynamic_axes:       <dict> 可变轴，默认只有 batch_size 可变
                                    当设置为 None 时表示所有轴均不可变。
            b_check_consistency: <boolean>

        一些建议：
            最好尝试在cpu上进行模型转换。
                如何做？一般可以在构建模型时，在其之前执行：
                    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
                来强制在cpu上构建模型。
            对于输入、输出是字典的模型，最好使用 utils.Model_Wrapper_for_dict_in_out 进行包裹。
    """
    model.eval()  # 若存在batchnorm、dropout层则一定要eval()!!!!再export

    # 推理torch模型，得到预期输出
    outputs = model(*inputs) if isinstance(inputs, (list, tuple,)) else model(inputs)
    outputs = ndl.traverse(var=[outputs], match_cond=lambda _, __, v: torch.is_tensor(v), action_mode="replace",
                           converter=lambda _, v: v.detach())[0]

    # 保存onnx模型
    inputs_nums = len(inputs) if isinstance(inputs, (list, tuple,)) else 1
    outputs_nums = len(outputs) if isinstance(outputs, (list, tuple,)) else 1
    input_names = [f'input_{i}' for i in range(inputs_nums)]
    output_names = [f'output_{i}' for i in range(outputs_nums)]
    dynamic_axes = kwargs.get("dynamic_axes", {i: [0] for i in input_names})  # 默认只有 batch_size 可变
    #
    os.makedirs(output_dir, exist_ok=True)
    inputs = tuple(inputs) if isinstance(inputs, list) else inputs
    # breakpoint()
    torch.onnx.export(
        model, inputs, f=os.path.join(output_dir, "model.onnx"),
        input_names=input_names, output_names=output_names, dynamic_axes=dynamic_axes , opset_version=10)  # , opset_version=11
    print(f'saved to {os.path.join(output_dir, "model.onnx")}')

    # 检验转换后的模型推理结果是否一致
    inputs_for_onnx = {k: v for k, v in zip(input_names, [inputs] if inputs_nums == 1 else inputs)}
    if isinstance(outputs, dict):
        expected_outputs = list(outputs.values())
    else:
        expected_outputs = [outputs] if outputs_nums == 1 else outputs
    outputs_for_onnx = run_onnx_model(model_path=os.path.join(output_dir, "model.onnx"), inputs=inputs_for_onnx)
    #
    if b_check_consistency:
        check_consistency(outputs_for_onnx, expected_outputs, tolerance=kwargs.get("tolerance", 1e-5))

    # record
    serializer.write(var=dict(inputs=inputs, outputs=expected_outputs),
                     output_dir=os.path.join(output_dir, "test_data_for_torch"))
    serializer.write(var=dict(inputs=inputs_for_onnx, outputs=outputs_for_onnx),
                     output_dir=os.path.join(output_dir, "test_data_for_onnx"))


if __name__ == '__main__':
    from kevin_toolbox.data_flow.file import json_
    from kevin_dl.utils.variable import root_dir
    from kevin_dl.workflow.config_handler import load_config, build_exp_from_config

    trial_dir = os.path.join(root_dir,
                             "result/reimplement_resnet_over_imagenet/resnet18/2023-08-31/for_imagenet_for_type5_dw/")

    # 加载配置
    cfg = load_config(
        file_path=os.path.join(root_dir, "kevin_dl/research/reimplement_resnet_over_imagenet/templates/basic_config"),
        b_parse_ref=True)

    # 更新部分超参数
    if True:
        # 更新
        hyper_paras = json_.read(file_path=os.path.join(trial_dir, "hyper_paras.json"))
        hyper_names = json_.read(file_path=os.path.join(trial_dir, "hyper_names.json"))
        for name in hyper_names:
            ndl.set_value(var=cfg, name=name, value=ndl.get_value(var=hyper_paras, name=name), b_force=False)

    # 只构建模型部分
    cfg = {"model": cfg["model"]}

    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # 强制在cpu上构建模型
    exp = build_exp_from_config(cfg=cfg)
    model = exp["model"]

    print(model)

    convert_torch_to_onnx(
        model=model, inputs=torch.randn((1, 3, 224, 224), dtype=torch.float32),
        output_dir=os.path.join(os.path.dirname(__file__), "temp"),
        dynamic_axes=None
    )
