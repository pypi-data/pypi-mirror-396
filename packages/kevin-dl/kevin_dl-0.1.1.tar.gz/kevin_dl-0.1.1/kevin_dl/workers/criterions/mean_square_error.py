import torch
import torch.nn.functional as F


def mean_square_error(pred, target, label_smoothing=0.0, **kwargs):
    if len(target.shape) < len(pred.shape) or target.shape[-1] != pred.shape[-1]:
        target = F.one_hot(target, num_classes=pred.shape[-1]).to(dtype=torch.float32)
    assert pred.shape == target.shape, f"pred.shape != target.shape"

    if label_smoothing is not None and label_smoothing != 0:
        k = target.size(-1)
        assert k > 1, f"label_smoothing is only supported for multi-class classification."
        target = (1 - label_smoothing) * target + label_smoothing / k
    return F.mse_loss(pred, target, **kwargs)
