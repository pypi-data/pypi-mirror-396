import copy
import torch
import torch.nn as nn
from kevin_toolbox.computer_science.algorithm import for_dict
from kevin_dl.workers.variable import MODELS


def build_blocks(**kwargs):
    """
        参数：
            c_in
    """
    # 默认参数
    paras = {
        # 必要参数
        "c_in": None,
        # 可选参数
        "blocks": [],
        # 默认参数（将作为全局选项）
        "block_type": ":shufflenet:blocks:Inverted_Residual",
        #
        "kernel_size": 3,
        "stride": 2,
    }
    # 获取参数
    paras.update(kwargs)

    # 校验参数
    assert paras["c_in"] is not None
    c_last = paras["c_in"]

    #
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
            c_last = block.paras["c_out"]
        blocks.add_module(f'group_{g_id}', temp)

    return blocks, c_last


if __name__ == '__main__':
    net, _ = build_blocks(
        c_in=32,
        blocks=[
            dict(block_num=2, c_out=64, stride=2, c_out_mid=64 // 2, c_out_skip=64 // 2, ),
            dict(block_num=2, c_out=128, stride=2, c_out_mid=128 // 2, c_out_skip=128 // 2, ),
        ],
        block_type=":shufflenet:blocks:Inverted_Residual",
    )
    print(net)
