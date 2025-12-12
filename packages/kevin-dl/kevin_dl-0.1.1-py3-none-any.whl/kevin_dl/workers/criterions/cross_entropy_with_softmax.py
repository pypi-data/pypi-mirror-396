import torch


def cross_entropy_with_softmax(pred, target, weight=None, reduction="mean"):
    """
        相较于官方的 torch.nn.CrossEntropyLoss()，其在 target 的两种模式下的值更加稳定。
            官方实现的两者可能存在微小差异。
    """
    if target.ndim == 1 or target.shape[-1] != pred.shape[-1]:
        # 对于记录index的label，应该先转换为 onehot 向量
        target = torch.nn.functional.one_hot(target.long(), pred.shape[-1])
    assert target.shape == pred.shape

    pred = torch.nn.functional.log_softmax(pred, dim=-1)
    res = -torch.sum(pred * target, dim=-1, keepdim=False)

    if weight is not None:
        assert len(weight) == len(res)
        res = res * weight

    if reduction == "mean":
        res = torch.mean(res)
    elif reduction == "sum":
        res = torch.sum(res)
    else:
        raise ValueError

    return res


class Cross_Entropy_with_Softmax(torch.nn.CrossEntropyLoss):

    def forward(self, input, target):
        assert self.label_smoothing == 0.0 and self.ignore_index == -100
        return cross_entropy_with_softmax(pred=input, target=target, weight=self.weight)


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

    loss_ls = []
    grad_ls = []
    for loss_func in [cross_entropy_with_softmax, torch.nn.CrossEntropyLoss(), Cross_Entropy_with_Softmax()]:
        y_ = torch.autograd.Variable(y, requires_grad=True)

        loss = loss_func(y_, label)
        loss_ls.append(loss)

        print(loss)

        loss.backward()
        print(y_.grad)
        grad_ls.append(y_.grad.clone())
    check_consistency(*loss_ls)
    check_consistency(*grad_ls)
