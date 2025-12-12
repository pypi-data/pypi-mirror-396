from enum import Enum


class Image_Format(Enum):
    TORCH_TENSOR = "torch.tensor"
    NP_ARRAY = "np.array"
    PIL_IMAGE = "pil.image"
