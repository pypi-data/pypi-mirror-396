import torch
import kevin_toolbox.nested_dict_list as ndl


def count_flops_and_param_nums(model, input_shape_wout_bz=None, input_shape_with_bz=None, inputs=None):
    """
        估算模型的flops数和参数数量

        注意：
            - 对于参数数量，可以只通过模型而不指定输入来估算，但可能会将模型中不实际参与计算的部分包含进来，导致估算不准
            - 对于 flops 数，必须同时指定模型和输入
            - 建议指定输入以获得更加准确的估计值

        指定输入的三种方式：
            - input_shape_wout_bz:          不包含 batch size 的形状
                                                比如 {"x_0": (3,96,96),"x_1": (3,96,96)}，将解释为
                                                {"x_0": <torch.tensor(1,3,96,96)>, "x_1": <torch.tensor(1,3,96,96)>}
                                                来作为模型的输入
            - input_shape_with_bz:          包含 batch size 的形状
            - inputs:                       直接指定输入
            以上三种只需选其一即可

        返回：
            <dict> with keys:
                - flops:                浮点运算次数，用来衡量模型计算复杂度
                - macs:                 1MACs包含一个乘法操作与一个加法操作，大约包含2FLOPs
                - total_params:         总参数量（一般以此为准）
                - trainable_params:     可训练参数量
                    当该 total_params 是使用 thop 估计时（更准确），trainable_params 将不进行估计
    """
    if input_shape_wout_bz is not None:
        input_shape_with_bz = \
            ndl.traverse(var=[input_shape_wout_bz], match_cond=lambda _, __, v: isinstance(v, (tuple,)),
                         action_mode="replace", converter=lambda _, v: (1, *v))[0]
    if input_shape_with_bz is not None:
        inputs = ndl.traverse(var=[input_shape_with_bz], match_cond=lambda _, __, v: isinstance(v, (tuple,)),
                              action_mode="replace", converter=lambda _, v: torch.randn(*v))[0]
    if isinstance(inputs, (list,)):
        inputs = tuple(inputs)

    res_s = dict(flops=None, macs=None, total_params=None, trainable_params=None)
    if inputs is not None:
        # macs
        try:
            from torchprofile import profile_macs
            res_s["macs"] = profile_macs(model, args=inputs)
        except:
            pass
        # flops
        for x in [inputs, (inputs,)]:
            try:
                from thop import profile
                res_s["flops"], res_s["total_params"] = profile(model, inputs=x, verbose=False)
            except:
                pass
            else:
                break
        if res_s["flops"] is not None and res_s["macs"] is not None and res_s["flops"] < res_s["macs"]:
            res_s["flops"] = None
    if res_s["total_params"] is None or res_s["total_params"] == 0:
        res_s["total_params"], res_s["trainable_params"] = 0, 0
        for p in model.parameters():
            res_s["total_params"] += p.numel()
            if p.requires_grad:
                res_s["trainable_params"] += p.numel()

    #
    res_s = {k: v if v is None else int(v) for k, v in res_s.items()}

    return res_s


if __name__ == '__main__':
    import torchvision.models as models

    # 加载预训练模型
    model = models.resnet18(pretrained=False)

    # 统计模型的MFLOPs
    res = count_flops_and_param_nums(model, input_shape_wout_bz=(3, 128, 128))

    print(f"{res}")
