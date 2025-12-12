import re
import copy
from kevin_toolbox.computer_science.algorithm import for_dict


def get_param_groups_from_settings(**kwargs):
    """
        根据 settings 中的设置和分组规则，生成 param_groups

        参数：
            settings:               <dict> 设置
                    其下包括两个键值对：
                    "for_all":          <dict of paras> 基础设置
                                            若非下面的 for_groups 中专门指定的参数，都将使用该设置。
                    "for_groups":       <dict> 指定参数的分组方式，以及各分组的设置
                                            形式为：
                                                {<regular expression>: <dict of paras>, ...}
                                            工作流程：
                                                首先将参数名满足 <regular expression> 正则表达式的模型参数分为一组，然后根据 <dict of paras> 为
                                                这组参数设置优化器，<dict of paras> 中缺少的设置将结合前面的 for_all 基础设置进行补全。
            named_parameters:       <list/generator of tuples> 模型参数
                                        形式为 [("para_name", para), ...]，具体可以参考 torch.model.named_parameters()

        返回：
            param_groups:           <list of dict> 参考 torch.optim.Optimizer 中的 self.param_groups。
                                        其中每个 dict 是一个分组，"params" 对应的值保存了分组的参数，其他键值对保存了分组的设置，
                                        例如：
                                            {"params": [var, ...], "lr": apply_lr, "weight_decay": weight_decay}
    """
    # 默认参数
    paras = {
        #
        "named_parameters": None,
        "settings": {"for_all": dict(), "for_groups": dict()}
    }

    # 获取参数
    paras = for_dict.deep_update(stem=paras, patch=kwargs)

    # 校验参数
    assert paras["named_parameters"] is not None and isinstance(paras["settings"], (dict,))
    settings = paras["settings"]
    for k, v in settings["for_groups"].items():
        settings["for_groups"][k] = for_dict.deep_update(stem=copy.deepcopy(settings["for_all"]), patch=v)

    # 将 named_parameters 中的参数分配给各个 group
    var_for_group_s = {k: [] for k in settings["for_groups"].keys()}
    var_for_all = []
    for name, var in paras["named_parameters"]:
        if not var.requires_grad:
            continue
        #
        for expression in var_for_group_s.keys():
            if re.search(pattern=expression, string=name) is not None:
                var_for_group_s[expression].append(var)
                break
        else:
            var_for_all.append(var)

    # 构建 params
    res = []
    #
    if len(var_for_all) > 0:
        res.append(for_dict.deep_update(stem=copy.deepcopy(settings["for_all"]), patch=dict(params=var_for_all)))
    #
    for k in sorted(var_for_group_s.keys()):
        if len(var_for_group_s[k]) == 0:
            continue
        res.append(for_dict.deep_update(stem=settings["for_groups"][k], patch=dict(params=var_for_group_s[k])))

    return res
