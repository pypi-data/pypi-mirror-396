import copy
import torch
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.nested_dict_list import value_parser as ndl_vp
from kevin_toolbox.nested_dict_list import name_handler as ndl_nh
from kevin_toolbox.computer_science.algorithm.scheduler import Trigger
from kevin_dl.workers.variable import MODELS, DATASETS, OPTIMIZERS, ALGORITHMS
from kevin_dl.workers.optimizers import Advanced_Optimizer
from kevin_dl.workers.datasets import build_dataset  # 不可删除


def build_exp_from_config(cfg, b_parse_ref=True):
    """
        遍历配置，根据其中的参数构建数据集和模型等实例
            对于配置中的键，若其为：
                - "model"       则遍历其所有节点，尝试以节点的值作为参数，使用 MODELS 来创建模型
                - "dataset"     使用 DATASETS 来创建数据集
                - "algorithm"   使用 ALGORITHMS 来创建算法执行器
                - "optimizer"   使用 OPTIMIZERS 来创建优化器
                - "trigger"     使用 Trigger 来创建触发器，并设置绑定对象

        参数：
            cfg:                <nested dict list> 配置
            b_parse_ref:        <boolean> 是否解释并替换配置中的引用值
                                    什么是引用值？
                                        配置是一个嵌套字典列表，对于值，若为字符串类型，且其中含有 "...<exp>{:x}..." 的形式，
                                        则表示解释该值时，需要将这部分替换为解释结果exp的x对应的值。
                                    默认为 True

        返回：
            exp:        <dict> 根据配置文件生成的当前实验的所有实例
    """
    DATASETS.get(":cv:Face_Liveness_Dataset:2.1")
    exp = copy.deepcopy(cfg)
    hook_s = dict()
    if b_parse_ref:
        # 替换引用值
        exp, _ = ndl_vp.parse_and_eval_references(var=exp, flag="exp",
                                                  converter_for_ref=lambda idx, v:
                                                  _parse(exp=v, pre_name=idx, hook_s=hook_s))
    exp = _parse(exp=exp, hook_s=hook_s)
    # 最后再将判断是否需要将其中的模型转移到gpu上。
    if torch.cuda.is_available() and "model" in hook_s:
        for name in hook_s["model"]:
            model = ndl.get_value(var=exp, name=name, default=None)
            if model is None:
                continue
            kwargs = ndl.get_value(var=cfg, name=name)
            if kwargs.get("b_use_gpu", True):
                model.cuda()
                model = torch.nn.DataParallel(model)
                exp = ndl.set_value(var=exp, name=name, value=model)
    return exp


def _parse(exp, pre_name="", hook_s=None):
    """
        遍历配置文件，根据其中的参数构建数据集和模型等实例
    """
    parse_key_set = {"model", "dataset", "algorithm", "optimizer", "trigger", "criterion"}
    # 由于 ndl.traverse() 不会遍历根节点，因此对于 pre_name 非空的情况，需要考虑 pre_name 中本身带有待解释的字段。
    #   因此当 pre_name 非空且包含待解释字段时，需要使用list对输入的 exp 进行包裹以便间接实现对 exp 的遍历。
    b_use_wrapper = False
    if len(pre_name) > 0 and any([i in pre_name for i in parse_key_set]):
        b_use_wrapper = True
        exp = [exp]

    def func(idx, value):
        nonlocal pre_name, hook_s, parse_key_set
        if b_use_wrapper:
            assert idx.startswith('@0')
            idx = idx[2:]
        root_node, method_ls, node_ls = ndl_nh.parse_name(name=pre_name + idx)
        for key in parse_key_set.intersection(set(node_ls)):
            builder = eval(f'build_{key}')
            try:
                obj = builder(**value)
                if hook_s is not None:
                    hook_s.setdefault(key, [])
                    hook_s[key].append(pre_name + idx)
                return obj
            except:
                pass
        return value

    ndl.traverse(var=exp, match_cond=lambda _, __, value: isinstance(value, (dict,)), action_mode="replace",
                 converter=func, b_use_name_as_idx=True, b_traverse_matched_element=False,
                 traversal_mode="dfs_post_order")
    if b_use_wrapper:
        exp = exp[0]

    return exp


def build_model(name, **kwargs):
    model = MODELS.get(name=name)(**kwargs)
    return model


def build_optimizer(name, named_parameters, **kwargs):
    optimizer = Advanced_Optimizer(
        builder=OPTIMIZERS.get(name=name),
        named_parameters=named_parameters, **kwargs
    )
    return optimizer


def build_algorithm(name, **kwargs):
    return ALGORITHMS.get(name=name)(**kwargs)


def build_trigger(target_s, **kwargs):
    return Trigger(target_s=target_s, **kwargs)


def build_criterion(coeff_s, **kwargs):
    from kevin_dl.workers.criterions import Mean_Adjustable_Variance_Loss, Cross_Entropy_with_Softmax

    criterion_s = dict()
    for k, w in coeff_s.items():
        if kwargs[k]["name"] == ":torch:nn:CrossEntropyLoss":
            builder = torch.nn.CrossEntropyLoss
        elif kwargs[k]["name"] == "mean_adjustable_variance_loss":
            builder = Mean_Adjustable_Variance_Loss
        elif kwargs[k]["name"] == "cross_entropy_with_softmax":
            builder = Cross_Entropy_with_Softmax
        else:
            raise ValueError(f"{kwargs[k]['name']} is not supported.")
        criterion_s[k] = builder(**kwargs[k].get("paras", dict()))
    #
    for k, v in criterion_s.items():
        if torch.cuda.is_available():
            criterion_s[k] = v.cuda()
    #
    criterion_s["coeff_s"] = coeff_s
    return criterion_s
