import os
import torch
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.data_flow.file import json_
from kevin_dl.deploy import convert_torch_to_onnx
from kevin_dl.workflow.state_manager import load_state


def build_onnx_from_ckpt(cfg_path, ckpt_path, output_dir, hyper_paras=None):
    from kevin_dl.workflow.config_handler import load_config, build_exp_from_config

    assert ckpt_path.endswith(".tar")
    # 加载配置
    cfg = load_config(file_path=cfg_path, b_parse_ref=True)

    # 更新部分超参数
    if hyper_paras is not None:
        if isinstance(hyper_paras, str):
            hyper_paras = json_.read(file_path=hyper_paras, b_use_suggested_converter=True)
        for name, value in hyper_paras.items():
            ndl.set_value(var=cfg, name=name, value=value, b_force=False)

    # 只构建模型部分
    cfg = {"model": cfg["model"]}
    exp = build_exp_from_config(cfg=cfg)

    # 加载预训练参数
    load_state(exp=exp, input_dir=os.path.dirname(ckpt_path),
               file_name=os.path.basename(ckpt_path).rsplit(".", 1)[0], b_load_non_state_part=False)

    model = exp["model"].module.cpu()

    print(model)

    convert_torch_to_onnx(
        model=model, inputs=torch.randn((1, 3, 224, 224), dtype=torch.float32),
        output_dir=output_dir,
        dynamic_axes=None
    )