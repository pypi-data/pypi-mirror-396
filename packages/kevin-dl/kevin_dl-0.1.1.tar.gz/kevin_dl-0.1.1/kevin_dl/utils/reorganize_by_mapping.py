import kevin_toolbox.nested_dict_list as ndl


def reorganize_by_mapping(var, mapping_ls):
    """
        将输入变量 var 按照指定映射规则记性进行重新组织

        参数:
            var:                变量
            mapping_ls:         <list of dict> 映射规则
                                    每个元素是一个包含以下键的字典：
                                    # 必要
                                        - "src": <name> or <list of name> of source in var
                                                    当有多个可选的名字时，依次从前到后尝试获取值。
                                        - "dst": <name> or <list of name> of target in res
                                                    当有多个值时，表示将 src 赋给多个目标
                                    # 可选
                                        - "default":    当所有的 src 在 var 中不存在时，将使用该默认值来赋给 res
    """
    if not mapping_ls:
        return var

    res = None
    for mapping in mapping_ls:
        for k in ["src", "dst"]:
            mapping[k] = mapping[k] if isinstance(mapping[k], (tuple, list,)) else [mapping[k]]
        #
        temp = []
        for n in mapping["src"]:
            try:
                temp.append(ndl.get_value(var=var, name=n))
                break
            except:
                pass
        if len(temp) == 0:
            if "default" in mapping:
                temp.append(mapping["default"])
            else:
                raise ValueError(f"Cannot find src of mapping {mapping} in var")
        mapping["src"] = temp[0]
        #
        for dst in mapping["dst"]:
            res = ndl.set_value(var=res, name=dst, value=mapping["src"], b_force=True)
    return res


if __name__ == '__main__':
    import time
    from kevin_toolbox.patches.for_test import check_consistency

    count = 0.0

    for _ in range(1000):
        # 正常使用映射
        mapping_ls = [
            {
                "src": (":args@0", ":kwargs:image"),  # image 参数
                "dst": ":args@0:image"
            },
            {
                "src": (":args@1", ":kwargs:b_blur"),  # b_blur 参数
                "dst": ":args@0:b_blur"
            },
            {
                "src": (":args@2", ":kwargs:seed"),  # seed 参数
                "dst": ":args@0:seed",
                "default": 114514
            }
        ]
        var = dict(args=[123, ], kwargs={"b_blur": True})
        start_time = time.time()
        res = reorganize_by_mapping(var=var, mapping_ls=mapping_ls)
        count += time.time() - start_time
        check_consistency(
            res,
            dict(args=[{"image": 123, "b_blur": True, "seed": 114514}, ], )
        )

    print(f'time: {count}')
