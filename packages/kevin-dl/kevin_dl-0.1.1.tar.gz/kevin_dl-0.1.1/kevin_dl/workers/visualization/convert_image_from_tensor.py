import torch
from kevin_dl.workers.transforms.for_images.utils import Image_Format


def convert_image_from_tensor(x, mean=None, std=None, output_format=Image_Format.PIL_IMAGE):
    # from kevin_dl.workers.algorithms.mixup.utils import normalize
    from kevin_dl.workers.transforms.for_images.utils import convert_format
    if torch.is_tensor(x):
        # x = normalize(x, mean=mean, std=std, b_reverse=True)
        x = x.clone()
        if std is not None:
            std = torch.as_tensor(std, dtype=x.dtype, device=x.device)
            if std.ndim == 1:
                std = std.view(-1, 1, 1)
            x.mul_(std)
        if mean is not None:
            mean = torch.as_tensor(mean, dtype=x.dtype, device=x.device)
            if mean.ndim == 1:
                mean = mean.view(-1, 1, 1)
            x.add_(mean)
    return convert_format(image=x, output_format=output_format)
