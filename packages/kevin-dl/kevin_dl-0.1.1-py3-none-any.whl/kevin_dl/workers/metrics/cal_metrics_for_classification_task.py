import torch
import numpy as np
from sklearn.metrics import (
    matthews_corrcoef,
    roc_auc_score,
    average_precision_score,
    precision_recall_fscore_support
)
from sklearn.preprocessing import label_binarize


def _get_values_by_key(values, keys, key_ls):
    temp = {k: v for k, v in zip(keys, values)}
    return [temp[k] for k in key_ls]


def cal_metrics_for_classification_task(predict, target, group_division_ratio=None, group_division_method="proportion",
                                        cls_ratio_s=None):
    """
        计算多分类数据集的各项综合指标
            包括：
                - each_class:   对每个类别的数据单独统计的指标
                    - precision:    精确率 \frac{TP}{TP + FP} 分母是所有被预测为该分类的样本
                    - recall:       准确率 \frac{TP}{TP + FN}  分母是真实值为该分类的样本
                    - f1:           F1分数是Precision和Recall的调和平均
                    - support:      每个类别的支持度（即每个类别的样本数量）
                    - ratio:        每个类别的支持度（即每个类别的样本数量）/ 总样本数
                    - roc_auc:      ROC曲线（tpr vs fpr）下的面积
                    - pr_auc:       PR曲线（precision vs recall）下的面积
                - overall:      对所有类别进行统计（主要是平均）
                    - macro_f1:     各个类别F1分数的平均值
                    - balanced_acc: 各个类别的平均准确率recall
                    - mcc:          预测标签与真实标签的皮尔逊相关系数
                    - roc_auc, pr_auc
                - major_group/minor_group:      对多数/少数类别群组进行统计
                    - macro_f1, balanced_acc, mcc, roc_auc, pr_auc
                    - cls_ls:       该分组包含哪些类别
                    - ratio, support
            支持类别不平衡（或者各类别重要性不同）的情况

        参数：
            predict:                <list/array/tensor> 模型的预测结果
                                        shape=[sample_nums, ] 或者 [sample_nums, cls_nums] 的列表
                                        建议使用后者，此时可以结合模型在各个类别上的分数计算各种 auc 指标
            target:                 <list/array/tensor> 数据的真实标签
                                        shape=[sample_nums, ] 或者 [sample_nums, cls_nums] 的列表
            group_division_ratio:   <float/list of float> 按各个类别的占比从高到低排列，分别从前往后（或从后往前）以总占比接近 group_division_ratio 为界，划分一个分组
                                        默认为 None，此时表示不进行分组统计。输出结果中将不包含 major_group 和 minor_group 的结果。
            group_division_method:  <str> 分组的方式。
                                        目前支持以下几种分组方式：
                                            - "proportion":         选取占比之和小于等于 group_division_ratio 的前/后 n 个类别作为一个分组
                                            - "rank":               选取占比大小排名在前/后 group_division_ratio 的类别作为一个分组
                                        默认为 "proportion"。
            cls_ratio_s:            <dict> 每个类别在数据集中的占比。
                                        默认为 None，此时将根据 target 进行统计。

        补充：
            为什么有 balanced_acc（平均 recall），但是却没有平均 precision 呢？
                - 回顾 precision 的定义，其反映的是“在预测为该类的所有样本中，有多少比例是真正属于它”。因此 Precision 与模型“预测出的正例数量”息息相关。
                如果模型对少数类几乎不去预测，那么对于少数类 Precision 会趋于 0，而对多数类如果预测过度，则 Precision 又可能很高。把它们简单平均，
                并不能消除模型在“忽略少数类”或“盲目过度预测某些类”两种极端之间的偏向。
    """
    assert group_division_method in ["proportion", "rank"]
    if group_division_ratio is not None and not isinstance(group_division_ratio, (list, tuple)):
        group_division_ratio = [group_division_ratio, ]
    if torch.is_tensor(predict):
        predict = predict.detach().cpu().numpy()
    if torch.is_tensor(target):
        target = target.detach().cpu().numpy()
    target, predict = np.asarray(target).reshape(-1), np.asarray(predict)
    predict = predict[..., None] if len(predict.shape) == 1 else predict
    assert len(target) == len(predict)

    y_true = target
    if predict.shape[0] == 1:
        y_pred = predict.reshape(-1)
        y_scores = None
    else:
        y_pred = np.argmax(predict, axis=1)
        y_scores = predict
    classes = np.unique(y_true)
    y_true_one_hot = label_binarize(y_true, classes=classes)

    metric_s = {
        "overall": dict(),  # 对所有类别的结果进行统计
        "major_group": dict(),  # 对多数类别群组进行统计（按各个类别的占比从高到低排列，分别从前往后以总占比接近 group_division_ratio 为界，划分一个分组）
        "minor_group": dict(),  # 对少数类别群组进行统计（...从后往前...）
        "each_class": dict(),  # 对每个类别分别进行统计
    }

    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=classes, zero_division=0)
    roc_auc = roc_auc_score(y_true_one_hot, y_scores, average=None, multi_class='ovr') if y_scores is not None else None
    pr_auc = average_precision_score(y_true_one_hot, y_scores, average=None) if y_scores is not None else None
    metric_s["each_class"].update(dict(
        precision=precision,  # 精确率 \frac{TP}{TP + FP} 分母是所有被预测为该分类的样本
        recall=recall,  # 准确率 \frac{TP}{TP + FN}  分母是真实值为该分类的样本
        f1=f1,  # F1分数是Precision和Recall的调和平均
        support=support,  # 每个类别的支持度（即每个类别的样本数量）。
        ratio=support / np.sum(support),  # 每个类别的支持度（即每个类别的样本数量）/ 总样本数
        roc_auc=roc_auc,  # ROC曲线（tpr vs fpr）下的面积
        pr_auc=pr_auc  # PR曲线（precision vs recall）下的面积
    ))

    # Overall metrics
    metric_s["overall"].update(dict(
        macro_f1=np.mean(f1),  # 各个类别F1分数的平均值
        balanced_acc=np.mean(recall),  # 各个类别的平均准确率recall
        mcc=matthews_corrcoef(y_true, y_pred),  # 预测标签与真实标签的皮尔逊相关系数
        roc_auc=np.mean(roc_auc) if roc_auc is not None else None,
        pr_auc=np.mean(pr_auc) if pr_auc is not None else None
    ))

    if group_division_ratio is not None:
        for gdr in group_division_ratio:
            # Group metrics
            if cls_ratio_s is not None:
                ratio_ls = np.asarray([cls_ratio_s[i] for i in classes])
            else:
                ratio_ls = metric_s["each_class"]["ratio"]
            cls_sample_ls_s = {i: y_true == i for i in classes}
            #
            for name, ori in [("major_group", -1), ("minor_group", 1)]:
                order = np.argsort(ori * ratio_ls)
                if group_division_method == "proportion":
                    cumsum = ratio_ls[order].cumsum()
                    temp = cumsum <= gdr
                elif group_division_method == "rank":
                    temp = np.asarray(range(len(order))) < (len(order) * gdr)
                if sum(temp) == 0:
                    metric_s[name][gdr] = None
                    continue
                cls_ls = classes[order][temp]
                group_ratio = sum(ratio_ls[order][temp])
                b_sample = 1
                for i in cls_ls:
                    b_sample = b_sample * cls_sample_ls_s[i]
                #
                metric_s[name][gdr] = dict(
                    cls_ls=cls_ls,
                    ratio=group_ratio,
                    support=np.sum(b_sample),
                    macro_f1=np.mean(_get_values_by_key(values=f1, keys=classes, key_ls=cls_ls)),
                    balanced_acc=np.mean(_get_values_by_key(values=recall, keys=classes, key_ls=cls_ls)),
                    mcc=matthews_corrcoef(y_true[b_sample], y_pred[b_sample]),
                    roc_auc=np.mean(
                        _get_values_by_key(values=roc_auc, keys=classes,
                                           key_ls=cls_ls)) if roc_auc is not None else None,
                    pr_auc=np.mean(
                        _get_values_by_key(values=pr_auc, keys=classes, key_ls=cls_ls)) if pr_auc is not None else None
                )

    return metric_s


if __name__ == "__main__":
    import kevin_toolbox.nested_dict_list as ndl
    from kevin_dl.workers.datasets.adjuster.utils.imbalanced_dist import exponential_decay

    res_ = ndl.serializer.read(
        input_path="~/Desktop/gitlab_repos/kevin_dl/result/sombrero/sombrero_v6p2/templates_0_2025_05_28_cifa10/26/infer_results/200.tar/test")
    out_s = cal_metrics_for_classification_task(
        predict=res_["pred"], target=res_["gt"],
        cls_ratio_s={i: j for i, j in enumerate(
            exponential_decay(gamma=0.1, cls_nums=10))},
        group_division_ratio=[0.1, 0.2, 0.3],
        group_division_method="rank"
    )
    print(out_s)
