import os
import shutil
import numpy as np
from tqdm import tqdm
import optuna
from optuna.study.study import TrialState
from kevin_dl.utils.variable import root_dir
from kevin_toolbox.data_flow.file import json_
from kevin_toolbox.patches import for_os
from kevin_toolbox.nested_dict_list import get_hash
from kevin_toolbox.patches.for_test import check_consistency
import argparse

"""
清理 study.db 以及 其中对应的 trials dir

使用方法：
cd <repo_dir>
cur=`pwd`
export PYTHONPATH=$cur:$PYTHONPATH
python kevin_dl/utils/clear_trials.py \
--study_name default \
--input_dir ~/Desktop/gitlab_repos/kevin_dl/result/quantify_image_quality_based_on_comparison/optimize_hyperparas/2023-08-19 \
"""

# ------------------------------ 接受外部参数 ------------------------------ #

out_parser = argparse.ArgumentParser(description="清理 study.db 以及 其中对应的 trials dir")
out_parser.add_argument("--input_dir", type=str, required=True)
out_parser.add_argument("--output_dir", type=str, required=False)
out_parser.add_argument("--study_name", type=str, required=False, default="default")
args = out_parser.parse_args().__dict__

if not args["output_dir"]:
    args["output_dir"] = args["input_dir"] + ".cleaned"

print(args)

# ------------------------------------------------------------ #

study_old = optuna.create_study(
    study_name=args["study_name"],
    storage=f'sqlite:///{os.path.join(args["input_dir"], "study.db")}',
    load_if_exists=True,
)

# 过滤
trial_ls = []
if len(study_old.trials) == 0:
    print(f'empty storage_file')
else:
    # 去除不完整实验
    print(f'remove incomplete experiments')
    count_s = dict(success=0, failed=0)
    for t in study_old.trials:
        count_s["failed"] += 1
        # 去掉失败、未跑完的试验
        if t.state in [TrialState.WAITING, TrialState.FAIL]:
            continue
        # 去掉缺少结果和超参数的
        if getattr(t, "values", None) is None or getattr(t, "params", None) is None:
            continue
        # 去除文件夹被删除的
        if not os.path.isdir(os.path.join(args["input_dir"], str(t.number))):
            continue
        trial_ls.append(t)
        count_s["success"] += 1
        count_s["failed"] -= 1
    print(count_s)

    hash_to_trial_s = dict()  # {<hash>: <trial>, ...}
    # 去掉超参数重复的
    print(f'remove duplicate experiments')
    for t in trial_ls:
        hash_ = get_hash(item=t.params, mode="sha256")
        if hash_ in hash_to_trial_s:
            # 如果已经存在，检查所得结果是否一致，若一致则只保留一个
            if np.max(np.abs(np.asarray(t.values) - np.asarray(hash_to_trial_s[hash_].values))) < 1e-6:
                continue
        hash_to_trial_s[hash_] = t
    print(f'pass {len(hash_to_trial_s)}')

    # 去掉超参数、用户属性不完整的
    print(f'remove experiments with incomplete attributes')
    for attr in ["params", "user_attrs"]:
        temp = set()
        for k, t in hash_to_trial_s.items():
            temp.update(getattr(t, attr).keys())
        for k, t in list(hash_to_trial_s.items()):
            if set(getattr(t, attr).keys()) != temp:
                hash_to_trial_s.pop(k)
    trial_ls = list(hash_to_trial_s.values())
    print(f'pass {len(hash_to_trial_s)}')

    print(f'\twe got trials: {len(study_old.trials)}\n'
          f'\t{len(trial_ls)} of which successfully passed the filters')

# 清理
if len(study_old.trials) == len(trial_ls):
    print(f'no need to clean up')
elif len(trial_ls) > 0:
    # 保存清理结果
    #   根据过滤后得到的 trial_ls 对 trials 目录中的结果进行重构（按照新的 study 中试验的序号来重新命名各个子文件夹）
    print(f'coping trials')
    for_os.remove(path=args["output_dir"], ignore_errors=True)
    os.makedirs(args["output_dir"], exist_ok=True)
    for new_trial_id, t in enumerate(tqdm(trial_ls)):
        shutil.copytree(src=os.path.join(args["input_dir"], str(t.number)),
                        dst=os.path.join(args["output_dir"], f'{new_trial_id}'))
    #   写入到新的 study.db 中
    print(f'saving to new storage')
    study_new = optuna.create_study(
        study_name=args["study_name"],
        storage=f'sqlite:///{os.path.join(args["output_dir"], "study.db")}',
        directions=study_old.directions,
    )
    for new_trial_id, t in enumerate(tqdm(trial_ls)):
        # 同步将 trial 中 的 number 也修改过来
        t.user_attrs["trial_dir"] = f'{new_trial_id}'
        study_new.add_trial(t)
