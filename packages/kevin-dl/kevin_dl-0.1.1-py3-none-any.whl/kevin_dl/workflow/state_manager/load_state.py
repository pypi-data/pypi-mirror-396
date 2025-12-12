import os
import torch
import warnings
import numpy as np
import kevin_toolbox.nested_dict_list as ndl
import kevin_toolbox.nested_dict_list.serializer as ndl_serializer


def load_state(exp, input_dir, file_name, b_load_non_state_part=True, b_verbose=False, logger=None, **kwargs):
    """
        加载实验的状态

        参数：
            exp:                                <nested dict list>
            input_dir:                          <path>
            file_name:                          <str>
            b_load_non_state_part:              <boolean> 是否更新exp中非状态部分
                                                    默认为 True
    """
    file_name = f'{file_name}'

    logger_info = (print if logger is None else logger.info) if b_verbose else lambda x: None
    logger_info(f'loading ...')

    state_s = ndl_serializer.read(input_path=os.path.join(input_dir, file_name) + ".tar")

    # for_exp
    for name, value in ndl.get_nodes(var=exp, level=-1, b_strict=True):
        if not callable(getattr(value, "load_state_dict", None)) and not b_load_non_state_part:
            continue
        #
        v = ndl.get_value(var=state_s["for_exp"], name=name, default=None)
        if v is None and ndl.get_value(var=state_s["for_exp"], name=name, default=-1) == -1:
            if b_verbose:
                print(f'failed to load {name}, because missing in the file')
            continue
        #
        if callable(getattr(value, "load_state_dict", None)):
            value.load_state_dict(v)
        else:
            ndl.set_value(var=exp, name=name, value=v)

    # for_rng
    if "for_rng" in state_s:
        np.random.set_state(state_s["for_rng"]["numpy"])
        torch.set_rng_state(state_s["for_rng"]["torch"])
        if torch.cuda.is_available() and state_s["for_rng"]["torch_cuda"] is not None:
            try:
                torch.cuda.set_rng_state(state_s["for_rng"]["torch_cuda"])
            except:
                warnings.warn(f'failed to load random state of torch_cuda')

    logger_info(f'loaded state from {os.path.join(input_dir, file_name) + ".tar"}')
