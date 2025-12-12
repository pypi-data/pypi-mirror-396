import torch


def cal_accuracy_for_classification_task(**kwargs):
    """
        为分类任务计算准确率
            支持 top-k 计算

        参数：
            predict:            <tensor> 分类任务的预测结果
                                    要求 shape 为 [batch_size, cls_nums]
                                        其中最后一个维度保存了各个类别的预测概率
            target:             <tensor> ground truth
                                    支持 shape 为 [batch_size]
                                        其中保存的是真实类别的 index
                                    同时支持 shape 为 [batch_size, cls_nums]
                                        其中最后一维是真实类别的 one-hot 表示
            top_ks_to_cal:      <list of int> 要计算哪几个 top_k 结果
                                    比如要计算 top-1 和 top-5 结果，则可以设置为 top_ks_to_cal=[1,5]
                                    默认为 [1]

        返回：
            res_s               <dict of acc> 对应 top_k 下的准确率
    """
    # 默认参数
    paras = {
        "predict": None,
        "target": None,
        "top_ks_to_cal": [1],
    }

    # 获取参数
    paras.update(kwargs)

    # 校验参数
    assert paras["predict"].ndim == 2 and paras["predict"].shape[0] == paras["target"].shape[0]
    predict = paras["predict"]
    batch_size = predict.shape[0]
    #
    if paras["target"].ndim > 1:  # one-hot 形式
        _, target = torch.max(paras["target"].data, dim=1)
    else:  # 已经是序号形式了
        target = paras["target"]
    assert target.ndim == 1
    #
    assert isinstance(paras["top_ks_to_cal"], (list, tuple,))
    max_top_k = max(paras["top_ks_to_cal"])
    assert max_top_k <= predict.shape[1]

    _, predict = torch.topk(predict, k=max_top_k, dim=1, largest=True, sorted=True)
    correct = predict == target.view(-1, 1).expand_as(predict)

    res = dict()
    for k in paras["top_ks_to_cal"]:
        acc = torch.sum(correct[:, :k]).float() / batch_size
        res[k] = float(acc.detach().cpu())

    return res


if __name__ == '__main__':
    print(
        cal_accuracy_for_classification_task(
            predict=torch.as_tensor([[0.1, 0.15, 0.2], [0.3, 0, 0.5], [0.9, 0.1, 0.6], [0.3, 0.1, 0.6]]),
            target=torch.as_tensor([1, 1, 0, 2]),
            top_ks_to_cal=[1, 3]
        )
    )
