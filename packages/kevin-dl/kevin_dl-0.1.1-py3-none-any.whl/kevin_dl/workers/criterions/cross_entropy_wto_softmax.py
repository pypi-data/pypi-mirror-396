import torch


def cross_entropy_wto_softmax(pred, target, reduction="mean", epsilon=1e-10):
    """
        无 softmax 的 cross entropy
    """
    if target.ndim == 1 or target.shape[-1] != pred.shape[-1]:
        # 对于记录index的label，应该先转换为 onehot 向量
        target = torch.nn.functional.one_hot(target.long(), pred.shape[-1])
    assert target.shape == pred.shape

    pred = torch.clamp(pred, min=epsilon, max=1.0)
    pred = torch.log(pred)
    res = -torch.sum(target * pred, dim=1)

    if reduction == "mean":
        res = torch.mean(res)
    elif reduction == "sum":
        res = torch.sum(res)
    else:
        raise ValueError

    return res


if __name__ == '__main__':
    from kevin_toolbox.patches.for_test import check_consistency

    y = torch.tensor([
        [0.1545, -0.5706, -0.0739],
        [0.2990, 0.1373, 0.0784],
        [0.1633, 0.0226, 0.1038]
    ])

    label = torch.tensor([0, 1, 0])

    label = torch.tensor([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0],
    ], dtype=torch.float32)


    def tst_func(pred, target):
        pred = torch.nn.functional.softmax(pred, dim=-1)
        return cross_entropy_wto_softmax(pred=pred, target=target)


    loss_ls = []
    grad_ls = []
    for loss_func in [tst_func, torch.nn.CrossEntropyLoss()]:
        y_ = torch.autograd.Variable(y, requires_grad=True)

        loss = loss_func(y_, label)
        loss_ls.append(loss)

        print(loss)

        loss.backward()
        print(y_.grad)
        grad_ls.append(y_.grad.clone())
    check_consistency(*loss_ls)
    check_consistency(*grad_ls)
