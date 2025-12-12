import copy
import torch
import torch.nn as nn
from kevin_toolbox.computer_science.algorithm import for_dict
from kevin_dl.workers.variable import MODELS


def build_blocks(**kwargs):
    """
        参数：
                conv:               <callable> 默认使用的卷积函数
                    若需要进一步指定 stem 和 skip 中使用的卷积函数，可以进一步补充以下参数：
                        conv_for_stem:      <callable> stem 部分使用的卷积函数
                        conv_for_skip:      <callable> skip connection 短连接部分使用的卷积函数
                norm:               <callable> 默认使用的 normalize 函数
                    若需要进一步指定 stem 和 skip 中使用的卷积函数，可以进一步补充以下参数：
                        norm_for_stem:      <callable> stem 部分使用的 normalize 函数
                        norm_for_skip:      <callable> skip connection 短连接部分使用的 normalize 函数
    """
    # 默认参数
    paras = {
        # 必要参数
        "c_in": None,
        # 可选参数
        "blocks": [],
        # 默认参数（将作为全局选项）
        "c_out": 32,
        "block_type": ":resnet:blocks:Pre_Act_Block",
        #
        "kernel_size": 3,
        "stride": 2,
        "conv": nn.Conv2d,
        "norm": nn.BatchNorm2d,
        "type_of_skip": "default",
    }
    # 获取参数
    paras.update(kwargs)

    # 校验参数
    assert paras["c_in"] is not None
    c_last = paras["c_in"]
    for k in ["conv_for_stem", "conv_for_skip"]:
        paras[k] = paras.get(k, paras["conv"])
        if isinstance(paras[k], (str,)): paras[k] = eval(paras[k])
    for k in ["norm_for_stem", "norm_for_skip"]:
        paras[k] = paras.get(k, paras["norm"])
        if isinstance(paras[k], (str,)): paras[k] = eval(paras[k])

    blocks = nn.Sequential()
    for g_id, cfg in enumerate(paras["blocks"]):
        block_builder = MODELS.get(name=cfg.get("block_type", paras["block_type"]))
        cfg = for_dict.deep_update(stem=copy.deepcopy(paras), patch=cfg)
        temp = nn.Sequential()
        for b_id in range(cfg["block_num"]):
            cfg["c_in"] = c_last
            if b_id > 0:
                cfg["stride"] = 1
            block = block_builder(**cfg)
            temp.add_module(f'block_{b_id}', block)
            c_last = block.paras["c_out_real"]
        blocks.add_module(f'group_{g_id}', temp)

    return blocks, c_last


if __name__ == '__main__':
    net, _ = build_blocks(
        c_in=32,
        blocks=[
            dict(block_num=2, c_out=64, stride=1),
            dict(block_num=2, c_out=128, stride=2),
        ],
        block_type=":resnet:blocks:Pre_Act_Bottle_Neck_Block",
        norm="nn.InstanceNorm2d",
    )
    print(net)
