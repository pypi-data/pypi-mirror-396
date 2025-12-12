import torch
import kevin_toolbox.nested_dict_list as ndl


def count_flops_of_model(model, input_shape_wout_bz=None, input_shape_with_bz=None, inputs=None):
    """
        注意 shape 必须采用 tuple ！！！！
    """
    if input_shape_wout_bz is not None:
        input_shape_with_bz = \
            ndl.traverse(var=[input_shape_wout_bz], match_cond=lambda _, __, v: isinstance(v, (tuple,)),
                         action_mode="replace", converter=lambda _, v: (1, *v))[0]
    if input_shape_with_bz is not None:
        inputs = ndl.traverse(var=[input_shape_with_bz], match_cond=lambda _, __, v: isinstance(v, (tuple,)),
                              action_mode="replace", converter=lambda _, v: torch.randn(*v))[0]
    assert inputs is not None

    if isinstance(inputs, (list,)):
        inputs = tuple(inputs)
    try:
        from torchprofile import profile_macs
        flops = profile_macs(model, args=inputs)
    except:
        from thop import profile
        flops, params = profile(model, inputs=inputs, verbose=False)
    return flops


if __name__ == '__main__':
    import torchvision.models as models

    # 加载预训练模型
    model = models.resnet50(pretrained=False)
    # model.cuda()
    # model = torch.nn.DataParallel(model)

    # 统计模型的MFLOPs
    flops = count_flops_of_model(model, input_shape_wout_bz=(3, 224, 224))
    # flops = count_flops_of_model(model, input_shape_wout_bz=[(3, 224, 224), ])

    print(f"MFLOPs: {flops / 1e6}")
