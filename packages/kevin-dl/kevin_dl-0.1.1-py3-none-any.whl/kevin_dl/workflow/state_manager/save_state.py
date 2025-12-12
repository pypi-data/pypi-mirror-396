import os
import time
import copy
import torch
import numpy as np
import kevin_toolbox.nested_dict_list as ndl
import kevin_toolbox.nested_dict_list.serializer as ndl_serializer


def save_state(exp, output_dir, file_name, b_save_non_state_part=False, b_verbose=False, logger=None, **kwargs):
    """
        保存实验的状态到文件 <output_dir>/<file_name>.tar 中
            保存 exp 的状态到 for_exp 字段下：
                - 对于 exp 中具有 state_dict() 方法的实例，比如 model 等，调用该方法获取状态
            保存随机生成器的状态到 for_rng 字段下：
                - 获取 torch 和 numpy 的随机生成器的状态

        参数：
            exp:                                <nested dict list>
            output_dir:                         <path>
            file_name:                          <str>
            b_save_non_state_part:              <boolean> 是否排除 exp 中非实例的部分，比如 epoch 等
                                                    默认为 False，当设置为 True 时可能引发意外的错误。
            user_attrs:                         <dict> 其他需要补充记录的信息
            b_verbose:                          <boolean>

        保存到文件中的数据结构：
            {
                "for_exp":{
                    # exp 的状态
                    "model": ...,
                    "dataset": ...,
                    ...,
                },
                "for_rng":{
                    # 随机生成器的状态
                    "torch": ...,
                    "torch_cuda": ...,
                    "numpy": ...,
                },
                "user_attrs":{
                    # 其他自定义信息，源自 user_attrs
                }
            }
    """
    file_name = f'{file_name}'

    logger_info = (print if logger is None else logger.info) if b_verbose else lambda x: None
    logger_info(f'saving .....')

    # for_exp
    exp_ = ndl.copy_(var=exp, b_deepcopy=False)
    for name, value in ndl.get_nodes(var=exp_, level=-1, b_strict=True):
        if callable(getattr(value, "state_dict", None)):
            value = value.state_dict()
        elif b_save_non_state_part:
            pass
        else:
            value = None
        ndl.set_value(var=exp_, name=name, value=value, b_force=False)

    # for_rng
    rng_ = dict(
        torch=torch.get_rng_state(),
        torch_cuda=torch.cuda.get_rng_state() if torch.cuda.is_available() else None,
        numpy=np.random.get_state(),
    )

    #
    state_s = dict(
        for_exp=exp_,
        for_rng=rng_,
        user_attrs=kwargs.get("user_attrs", None)
    )

    if not os.path.exists(os.path.join(output_dir, file_name + ".tar")):
        count = 0
        while count < 3:
            try:
                ndl_serializer.write(
                    var=state_s, output_dir=os.path.join(output_dir, file_name),
                    settings=[
                        {"match_cond": "<level>-1",
                         "backend": (":skip:simple", ":numpy:npy", ":torch:tensor", ":torch:all")},
                    ],
                    traversal_mode="bfs", b_pack_into_tar=True, strictness_level="low")

                logger_info(f'saved state to {os.path.join(output_dir, file_name) + ".tar"}')
                break
            except:
                count += 1
                logger_info(f'failed to save state, we will try again in 1s')
                time.sleep(1)
    else:
        logger_info(f'state already saved in {os.path.join(output_dir, file_name) + ".tar"}')
