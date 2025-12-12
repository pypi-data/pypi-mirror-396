from kevin_toolbox.computer_science.algorithm import for_seq


def merge_contents(content_ls, b_exclude_columns_non_shared=True, b_exclude_rows_with_missing_value=True,
                   output_keys=None):
    assert len(content_ls) > 0

    if b_exclude_columns_non_shared:
        keys = set(content_ls[0].keys()).intersection(*[set(i.keys()) for i in content_ls[1:]])
    else:
        keys = set(content_ls[0].keys()).union(*[set(i.keys()) for i in content_ls[1:]])
    if output_keys is not None:
        keys = keys.intersection(set(output_keys))
    row_nums = [len(list(content.values())[0]) for content in content_ls]

    res = {k: for_seq.flatten_list(ls=[content.get(k, [None] * num) for content, num in zip(content_ls, row_nums)],
                                   depth=1) for k in keys}

    # 剔除存在空缺的行
    if b_exclude_rows_with_missing_value:
        invalid_ids = set(
            for_seq.flatten_list(ls=[[i for i, v in enumerate(v_ls) if v is None] for v_ls in res.values()]))
        for i in sorted(list(invalid_ids), reverse=True):
            for v in res.values():
                v.pop(i)

    return res


if __name__ == '__main__':
    res = merge_contents(content_ls=[
        dict(a=[1, 2, 3], b=[4, 5, 6]),
        dict(a=[1, 2, 3], c=[7, None, 9])
    ], b_exclude_columns_non_shared=True, b_exclude_rows_with_missing_value=False)

    print(res)

    res = merge_contents(content_ls=[
        dict(a=[1, 2, 3], b=[4, 5, 6]),
        dict(a=[1, 2, 3], c=[7, None, 9])
    ], b_exclude_columns_non_shared=True, b_exclude_rows_with_missing_value=True)

    print(res)
