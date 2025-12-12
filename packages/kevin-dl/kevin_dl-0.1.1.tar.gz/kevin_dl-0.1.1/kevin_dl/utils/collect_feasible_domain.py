import kevin_toolbox.nested_dict_list as ndl


def collect_feasible_domain(var):
    """
        从 var 中收集定义域类型的节点

        参数：
            var:                <ndl> 当其中的节点满足 <feasible_domain> 格式要求时，将整理到输出中。
                                    <feasible_domain> 格式要求：
                                        1. 是一个 dictionary
                                        2. 包含 "p_type"  字段
                                            "p_type" 表示定义域类型，常见值包括："float" "int" "categorical" 等
    """

    res_s = dict()

    def func(idx, v):
        nonlocal res_s
        res_s[idx] = v
        return v

    ndl.traverse(var=var, match_cond=lambda _, __, v: isinstance(v, (dict,)) and "p_type" in v,
                 action_mode="replace", converter=func, b_use_name_as_idx=True)

    return res_s
