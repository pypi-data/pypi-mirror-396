import os
from tqdm import tqdm
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.data_flow.file import json_


def infer_model_over_dataset(config_path, ckpt_path, dataset=None, dataloader=None, hyper_paras=None, label_func=None, inputs_func=None,
                             pred_func=None):
    assert dataset is not None or  dataloader is not None, \
        f"dataset or dataloader must be provided"
    from kevin_dl.workflow.config_handler import load_config, build_exp_from_config
    from kevin_dl.workflow.state_manager import load_state
    from kevin_dl.workflow.utils import set_seed

    label_func = (lambda x: x[1]) if label_func is None else label_func

    # 获取需要更新的超参数
    if hyper_paras is not None and isinstance(hyper_paras, str):
        hyper_paras = json_.read(file_path=hyper_paras, b_use_suggested_converter=True)

    # 构建 cfg
    cfg = load_config(file_path=config_path, update_part_s=hyper_paras, b_parse_ref=True)
    # 构建 exp
    set_seed(seed=cfg["seed"])
    exp = build_exp_from_config(cfg=cfg)
    exp = {k: v for k, v in exp.items() if k in ["dataset", "model"]}

    # 恢复状态
    load_state(exp=exp, input_dir=os.path.dirname(ckpt_path), file_name=os.path.basename(ckpt_path).rsplit('.', 1)[0],
               b_verbose=True, b_load_non_state_part=False)
    exp["model"].eval()

    # 在给定数据集上进行推理
    pd_ls, gt_ls = [], []
    if dataset is not None:
        inputs_func = (lambda x: ((x[0][None, ...],), dict())) if inputs_func is None else inputs_func
        pred_func = (lambda x: x[0].detach().cpu().numpy()) if pred_func is None else pred_func
        #
        if isinstance(dataset, (str,)):
            assert dataset in ["train", "val", "test"]
            dataset = ndl.get_value(var=exp, name=f":dataset:for_{dataset}:dataset", default=None)
            assert dataset is not None
        for idx in tqdm(range(len(dataset))):
            data = dataset[idx]
            gt_ls.append(label_func(data))
            #
            args, kwargs = inputs_func(data)
            pd = exp["model"](*args, **kwargs)
            pd = pred_func(pd)
            pd_ls.append(pd)
    else:  # use dataloader
        inputs_func = (lambda x: ((x[0],), dict())) if inputs_func is None else inputs_func
        pred_func = (lambda x: list(x.detach().cpu().numpy())) if pred_func is None else pred_func

        if isinstance(dataloader, (str,)):
            assert dataloader in ["train", "val", "test"]
            dataloader = ndl.get_value(var=exp, name=f":dataset:for_{dataloader}:data_loader", default=None)
            assert dataloader is not None
        for data in tqdm(dataloader):  # exp["dataset"]["for_train"]
            gt_ls.extend(label_func(data).tolist())
            #
            args, kwargs = inputs_func(data)
            pd = exp["model"](*args, **kwargs)
            pd = pred_func(pd)
            pd_ls.extend(pd)

    res_s = {"pred": pd_ls, "gt": gt_ls}
    return res_s


if __name__ == '__main__':
    res = infer_model_over_dataset(
        config_path="~/Desktop/gitlab_repos/kevin_dl/result/sombrero/mixup_pro_over_resnet18_over_cifa100/templates_1b_04_2025_01_23/config",
        hyper_paras="~/Desktop/gitlab_repos/kevin_dl/result/sombrero/mixup_pro_over_resnet18_over_cifa100/templates_1b_04_2025_01_23/12/hyper_paras.json",
        ckpt_path="~/Desktop/gitlab_repos/kevin_dl/result/sombrero/mixup_pro_over_resnet18_over_cifa100/templates_1b_04_2025_01_23/12/checkpoints/158.tar",
        dataset="test"
    )
    print(res)
