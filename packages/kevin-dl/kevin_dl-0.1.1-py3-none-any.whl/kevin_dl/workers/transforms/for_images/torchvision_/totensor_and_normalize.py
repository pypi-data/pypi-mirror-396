import torch
import torchvision.transforms.functional as F
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class ToTensor_and_Normalize(Base_Transform):
    """
        归一化
    """
    name = ":for_images:torchvision:ToTensor_and_Normalize"

    def cal(self, input_s, mean=(0,), std=(1,), inplace=False, **kwargs):
        """
            参数：
                input_s:                <dict>
                                            其中包含：
                                                image:      <torch.tensor> shape [C, H, W]
                mean:                   <sequence> 归一化的均值。应该是一个包含每个通道的均值的序列。
                std:                    <sequence> 归一化的标准差。应该是一个包含每个通道的标准差的序列。
                inplace:                <boolean> 是否原地操作。默认为False，表示创建新的图像。
        """
        image = convert_format(image=input_s["image"], output_format=Image_Format.TORCH_TENSOR).to(
            dtype=torch.float).div(255)
        if len(mean) == 1:
            mean = list(mean) * image.shape[-3]
        if len(std) == 1:
            std = list(std) * image.shape[-3]

        res = F.normalize(image, mean, std, inplace)
        input_s["image"] = res

        return input_s


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format, Image_Format


    image = Image.open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "test_data", "ILSVRC2012_val_00040001.JPEG"))

    output_s = TRANSFORMS.get(name=":for_images:torchvision:ToTensor_and_Normalize")(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )(
        input_s=dict(image=image)
    )

    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()

    # 验证一致性
    from kevin_toolbox.patches.for_test import check_consistency
    import torchvision.transforms as transforms

    output_2 = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])(image)
    check_consistency(output_2, output_s["image"])
