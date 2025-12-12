import os
import math
import inspect
import torch
from kevin_toolbox.computer_science.algorithm.for_dict import deep_update
import kevin_toolbox.nested_dict_list as ndl
from kevin_dl.workers.datasets.utils import generate_k_fold_indices
from kevin_dl.workers.datasets.utils.variable import Task_Type
from kevin_dl.workers.variable import DATASETS


def build_dataset(dataset, subset=None, adjuster=None, data_loader=None, task_type=Task_Type.Train,
                  seed=114514):
    """
        构建数据集

        参数：
            dataset:            <Dataset/dict of paras> 数据集/用于构建数据集的参数
            subset:             <Dataset/dict of paras/None> 子集/用于进一步构建子集的参数
                                    包含：
                                        n_splits:           <int> 将数据分成几份
                                        pick_split_idx:     <int> 选取其中第几份
                                        b_inverse_pick:     <boolean> 是否进行反选
            adjuster:           <Dataset/dict of paras/None> 数据比例调整器
                                    具体参见 adjuster 模块下相关调整器的介绍，比如 :adjuster:Proportion_Adjuster
            data_loader:        <DataLoader/dict of paras/None> data_loader/用于进一步构建 data_loader 的参数
            task_type:          <str> 任务类型，有 "train" "test" "val" 可选
            seed:               <int> 随机种子

        工作流程：
            dataset ==> subset ==> adjuster ==> data_loader
            当中间有节点缺失。直接跳到下一节点
    """
    if isinstance(dataset, (dict,)):
        paras = deep_update(stem=ndl.copy_(var=dataset["paras"], b_deepcopy=True),
                           patch=dict(seed=seed))
        paras.setdefault("task_type", task_type)
        dataset = DATASETS.get(name=dataset["name"])(**paras)
    last_ = dataset

    if isinstance(subset, (dict,)):
        pick_indices, other_indices = generate_k_fold_indices(
            size=len(dataset), n_splits=subset["n_splits"],
            val_split_idx=subset.get("pick_split_idx", 0),
            shuffle=True, seed=seed
        )
        indices = other_indices if subset.get("b_inverse_pick", False) else pick_indices
        subset = torch.utils.data.Subset(dataset, indices)
    last_ = last_ if subset is None else subset

    if isinstance(adjuster, (dict,)):
        temp = DATASETS.get(name=adjuster["name"])
        paras = deep_update(stem=ndl.copy_(var=adjuster["paras"], b_deepcopy=True),
                            patch=dict(src_dataset=last_, seed=seed))
        paras.setdefault("task_type", task_type)
        if inspect.isclass(temp):
            adjuster = temp(**paras)
        elif inspect.isfunction(temp):
            idx_map_ls = temp(**paras)
            adjuster = torch.utils.data.Subset(last_, idx_map_ls)
        else:
            raise ValueError(f"{adjuster['name']} is not a class or function")
    last_ = last_ if adjuster is None else adjuster

    # data_loader.update(dict(num_workers=0))  # set it if use pdb to debug
    if isinstance(data_loader, (dict,)):
        if "num_workers" not in data_loader or data_loader["num_workers"] == -1:
            data_loader["num_workers"] = min(math.ceil(int(os.cpu_count() * 0.85)), os.cpu_count() - 1,
                                             data_loader["batch_size"] // 2 + 1)
        data_loader = torch.utils.data.DataLoader(
            dataset=last_,
            **data_loader
        )

    return dict(dataset=dataset, subset=subset, adjuster=adjuster, data_loader=data_loader)


if __name__ == '__main__':
    import os
    from kevin_toolbox.nested_dict_list import serializer
    from kevin_dl.utils.variable import root_dir

    cfgs = serializer.read(
        input_path=os.path.join(
            root_dir,
            "kevin_dl/workers/datasets/cv/image_quality/configs/ILSVRC2012mini_with_Randomly_Blurred")
    )

    for k, v in cfgs.items():
        out = build_dataset(**v)
        print(k, len(out['subset'] if 'subset' in out else out['dataset']), len(out['data_loader']))
        print(out)
