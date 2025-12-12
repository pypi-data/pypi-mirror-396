import numpy as np
import torch
from PIL import Image
from torchvision.transforms.functional import pil_to_tensor, to_pil_image
from kevin_dl.workers.transforms.for_images.utils import get_format, Image_Format


def tensor_to_np_array(tensor):
    return np.transpose(tensor.cpu().detach().numpy(), (1, 2, 0))


def np_array_to_tensor(np_array):
    return torch.from_numpy(np_array).permute(2, 0, 1)


CONVERT_PROCESS_S = {
    (Image_Format.TORCH_TENSOR, Image_Format.NP_ARRAY): tensor_to_np_array,  # (from, to): process
    (Image_Format.NP_ARRAY, Image_Format.TORCH_TENSOR): np_array_to_tensor,
    (Image_Format.PIL_IMAGE, Image_Format.NP_ARRAY): np.array,
    (Image_Format.NP_ARRAY, Image_Format.PIL_IMAGE): Image.fromarray,
    (Image_Format.TORCH_TENSOR, Image_Format.PIL_IMAGE): to_pil_image,
    (Image_Format.PIL_IMAGE, Image_Format.TORCH_TENSOR): pil_to_tensor
}


def convert_format(image, output_format, input_format=None):
    """
        在各种图片格式之间进行转换

        参数：
            image:
            input_format:       <str> 描述输入的格式。
                                    默认为 None，将根据 var 实际格式进行推断。
            output_format:      <str/list of str> 输出的目标格式。
                                    目前支持：
                                        - torch.tensor
                                        - np.array
                                        - pil.image
                                    当输入是一个 tuple/list 时，将输出其中任一格式，具体规则为：
                                        - 当 input_format 不在可选的输出格式中时，优先按照第一个输出格式进行转换
                                        - 当 input_format 在可选的输出格式中时，不进行转换。
    """
    if input_format is None:
        input_format = get_format(image=image)
    input_format = Image_Format(input_format)
    if not isinstance(output_format, (list, tuple,)):
        output_format = [output_format]
    output_format = [Image_Format(i) for i in output_format]

    if input_format in output_format:
        return image
    else:
        return CONVERT_PROCESS_S[(input_format, output_format[0])](image)
