import numpy as np
from PIL import Image
import torch
from kevin_dl.workers.transforms.for_images.utils import Image_Format


def get_format(image):
    if isinstance(image, np.ndarray):
        res = Image_Format.NP_ARRAY
    elif isinstance(image, torch.Tensor):
        res = Image_Format.TORCH_TENSOR
    elif Image.isImageType(image):
        res = Image_Format.PIL_IMAGE
    else:
        res = None
    return res
