import os
from collections import defaultdict
from kevin_toolbox.data_flow.file import kevin_notation


def find_trials(input_dir):
    res_s = defaultdict(dict)  # {<trial_dir>: {"checkpoints": [...], "log": {"test": <dict>, ...}}}
    trial_dir_ls = []
    for root, dirs, files in os.walk(input_dir):
        # 检查是否存在名为 checkpoints 的文件夹
        if 'checkpoints' in dirs:
            trial_dir_ls.append(os.path.relpath(root, input_dir))
    print(f"Found {len(trial_dir_ls)} trials in {input_dir}")

    for trial_dir in trial_dir_ls:
        res_s[trial_dir]["ckpt"] = [file for file in
                                    os.listdir(os.path.join(input_dir, trial_dir, 'checkpoints')) if
                                    file.endswith(".tar")]
        res_s[trial_dir]["ckpt_prefix"] = os.path.join(trial_dir, 'checkpoints')
        for task_type in ["train", "test", "val"]:
            file_path = os.path.join(input_dir, trial_dir, f"{task_type}_log.kvt")
            if os.path.isfile(file_path):
                res_s[trial_dir].setdefault("log", dict())
                _, res_s[trial_dir]["log"][task_type] = kevin_notation.read(file_path=file_path)

    return res_s


if __name__ == "__main__":
    import kevin_toolbox.nested_dict_list as ndl

    temp = find_trials(
        input_dir="~/Desktop/gitlab_repos/kevin_dl/result/sombrero/temp/templates_0_mixup_cifa10_exponential-decay")
    # print(temp)
    print(ndl.get_value(var=list(temp.values())[0], name=":log:test").keys())
