import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional as F
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class RandomResizedCrop(Base_Transform):
    """
        归一化
    """
    name = ":for_images:torchvision:RandomResizedCrop"

    def cal(self, input_s, size=None, scale=(0.08, 1.0), ratio=(3. / 4., 4. / 3.),
            interpolation=F.InterpolationMode.BILINEAR, **kwargs):
        """
            参数：
                input_s:                <dict>
                                            其中包含：
                                                image:      <torch.tensor> shape [C, H, W]
                size:                   <int/sequence> 期望输出的图像大小。可以是一个整数，表示输出为正方形图像的边长；
                                            也可以是一个包含两个整数的元组，表示输出图像的高度和宽度。
                scale:                  <tuple> 随机缩放范围，用于选择裁剪区域的大小。应该是一个包含两个浮点数的元组，
                                            表示缩放范围的下限和上限。默认为(0.08, 1.0)。
                ratio:                  <tuple> 随机宽高比范围，用于选择裁剪区域的宽高比。应该是一个包含两个浮点数的元组，
                                            表示宽高比范围的下限和上限。默认为(3/4, 4/3)。
                interpolation:          <int> 插值方法的整数值，用于缩放图像。默认为 InterpolationMode.BILINEAR。
        """
        image = convert_format(image=input_s["image"], output_format=Image_Format.TORCH_TENSOR)
        if size is None:
            size = list(image.shape[-2:])
        elif isinstance(size, (int,)):
            size = [size] * 2
        assert len(size) == len(scale) == len(ratio) == 2
        assert scale[0] <= scale[1] and ratio[0] <= ratio[1]



        # 需要截取的矩形框 (i, j, h, w)
        rect = transforms.RandomResizedCrop.get_params(image, scale, ratio)
        #
        res = F.resized_crop(image, *rect, size, interpolation)
        input_s["image"] = res
        input_s["details"] = dict(crop_rect=rect, raw_shape=tuple(image.shape))

        return input_s


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format, Image_Format

    image = Image.open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "test_data", "ILSVRC2012_val_00040001.JPEG"))

    output_s = TRANSFORMS.get(name=":for_images:torchvision:RandomResizedCrop")(
        size=496
    )(
        input_s=dict(image=image)
    )

    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
