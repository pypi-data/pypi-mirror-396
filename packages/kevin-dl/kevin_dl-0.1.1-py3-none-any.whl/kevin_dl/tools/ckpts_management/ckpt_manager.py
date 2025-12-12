import os
import re
import shutil
from collections import defaultdict
from enum import Enum
import numpy as np
from kevin_dl.tools.ckpts_management import find_trials
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.patches import for_os


class Task_Type(Enum):
    REMOVE = "remove"
    MOVE_TO_BAK = "move_to_bak"
    RECOVER_FROM_BAK = "recover_from_bak"
    KEEP = "keep"


class Ckpt_Manager:
    def __init__(self, input_dir, bak_dir=None):
        assert os.path.isdir(input_dir), f"input_dir: {input_dir} does not exist"

        self.input_dir = input_dir
        self.bak_dir = bak_dir if bak_dir is not None else input_dir + "_bak"
        os.makedirs(self.bak_dir, exist_ok=True)
        self.trial_s = find_trials(input_dir=input_dir)
        if self.bak_dir is not None:
            assert os.path.isdir(self.bak_dir), f"bak_dir: {self.bak_dir} does not exist"
            bak_s = find_trials(input_dir=self.bak_dir)
            for trial_name, it in bak_s.items():
                self.trial_s[trial_name]["ckpt"].extend(it["ckpt"])
        self.task_s = defaultdict(set)

    def add_task(self, task_type, match_cond=None):
        """
            参数：
                match_cond:         <str/func> 匹配条件
                                        当输入值为 str 时，将会解释为 regular_pattern 并与每个 ckpt 名进行匹配（不包含.tar后缀）
                                        当输入值为 tuple 时，支持以下方式：
                                            - (<key>, "argmax", <key>)
                                            - (<key>, "argmin", <key>)
                                            比如 (":test:epoch", "argmax", ":test:acc_top_1") 表示取 acc_top_1 最大时的 epoch 对应的 ckpt
                                        当输入值为 func 时，要求形如 func(ckpt_name, log_s, trial_dir) ==> boolean，
                                            其中 ckpt_name 不包含.tar后缀。
                task_type:          <str> 任务种类
                                        有以下可选项：
                                            - remove\move_to_bak\recover_from_bak\keep

        """
        task_type = Task_Type(task_type)

        res_ls = []
        for trial_dir, it in self.trial_s.items():
            if isinstance(match_cond, str):
                # pattern matching against ckpt name (without .tar)
                pattern = re.compile(match_cond)
                for ckpt_name in it["ckpt"]:
                    if pattern.match(ckpt_name.rsplit(".", 1)[0]):
                        res_ls.append(os.path.join(it["ckpt_prefix"], ckpt_name))

            elif isinstance(match_cond, tuple) and len(match_cond) == 3:
                # Handle argmax/argmin based on logs
                assert match_cond[1] in ["argmax", "argmin"]
                key_metric = ndl.get_value(var=it["log"], name=match_cond[-1])
                key_index = np.asarray(ndl.get_value(var=it["log"], name=match_cond[0]))
                if match_cond[1] == "argmax":
                    key_index = key_index[key_metric == np.max(key_metric)]
                else:  # "argmin"
                    key_index = key_index[key_metric == np.min(key_metric)]
                for ckpt_name in it["ckpt"]:
                    for idx in key_index:
                        if ckpt_name.rsplit(".", 1)[0] == str(idx):
                            res_ls.append(os.path.join(it["ckpt_prefix"], ckpt_name))
                            break

            elif callable(match_cond):
                for ckpt_name in it["ckpt"]:
                    if match_cond(ckpt_name.rsplit(".", 1)[0], it["log"], trial_dir):
                        res_ls.append(os.path.join(it["ckpt_prefix"], ckpt_name))
            else:
                raise ValueError(f"unsupported match_cond: {match_cond}")

        res_set = set(res_ls)
        if task_type == Task_Type.KEEP:
            # 保持不动
            for k in [Task_Type.REMOVE, Task_Type.MOVE_TO_BAK, Task_Type.RECOVER_FROM_BAK]:
                self.task_s[k].difference_update(res_set)
        else:
            for k in [Task_Type.REMOVE, Task_Type.MOVE_TO_BAK, Task_Type.RECOVER_FROM_BAK]:
                if task_type != k:
                    self.task_s[k].difference_update(res_set)
            self.task_s[task_type].update(res_set)

    def clear(self):
        self.task_s.clear()

    def dry_run(self, task_type=None):
        self.run(task_type=task_type, b_dry_run=True)

    def run(self, task_type=None, b_dry_run=False):
        # 执行顺序 RECOVER_FROM_BAK ==> MOVE_TO_BAK ==> REMOVE
        if b_dry_run:
            print("Dry run mode...")

        if self.task_s[Task_Type.RECOVER_FROM_BAK]:
            print(
                f"recovering from bak..., there are {len(self.task_s[Task_Type.RECOVER_FROM_BAK])} files to be recovered.")
            for i in sorted(self.task_s[Task_Type.RECOVER_FROM_BAK]):
                src = os.path.join(self.bak_dir, i)
                dst = os.path.join(self.input_dir, i)
                if os.path.exists(src):
                    if not b_dry_run:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.move(src=src, dst=dst)
                    print(f"recovered '{i}' from bak")
                else:
                    print(f"'{i}' does not exist, skip!")
        if self.task_s[Task_Type.MOVE_TO_BAK]:
            print(f"moving to bak..., there are {len(self.task_s[Task_Type.MOVE_TO_BAK])} files to be moved.")
            for i in sorted(self.task_s[Task_Type.MOVE_TO_BAK]):
                src = os.path.join(self.input_dir, i)
                dst = os.path.join(self.bak_dir, i)
                if os.path.exists(src):
                    if not b_dry_run:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.move(src=src, dst=dst)
                    print(f"moved '{i}' to bak")
                else:
                    print(f"'{i}' does not exist, skip!")
        if self.task_s[Task_Type.REMOVE]:
            print(f"removing..., there are {len(self.task_s[Task_Type.REMOVE])} files to be removed.")
            for i in sorted(self.task_s[Task_Type.REMOVE]):
                src = os.path.join(self.input_dir, i)
                if os.path.exists(src):
                    if not b_dry_run:
                        for_os.remove(src)
                    print(f"removed '{i}'")
        if not b_dry_run:
            self.clear()


if __name__ == "__main__":
    ckpt_manager = Ckpt_Manager(
        input_dir="~/Desktop/gitlab_repos/kevin_dl/result/sombrero/"
                  "temp/templates_0_mixup_cifa10_exponential-decay")
    ckpt_manager.add_task(match_cond=".*", task_type="move_to_bak")
    ckpt_manager.add_task(match_cond="200", task_type="keep")
    ckpt_manager.run()
    ckpt_manager.add_task(match_cond="100", task_type="recover_from_bak")
    ckpt_manager.run()
    ckpt_manager.add_task(match_cond=(":test:epoch", "argmax", ":test:acc_top_1"), task_type="recover_from_bak")
    ckpt_manager.run()
