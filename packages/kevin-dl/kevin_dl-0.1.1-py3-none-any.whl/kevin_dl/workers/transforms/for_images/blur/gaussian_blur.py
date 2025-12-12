import numpy as np
import cv2
import math
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class Gaussian_Blur(Base_Transform):
    """
        动态模糊
    """
    name = ":for_images:blur:Gaussian_Blur"

    def cal(self, input_s, kernel_size=None, sigma=3, **kwargs):
        """
            参数：
                input_s:                <dict>
                                            其中包含：
                                                image:      <np.array> shape [H, W, C]
                kernel_size:            <int/ list of integers> 模糊矩阵的卷积核大小
                                            当设置为 None 时，将根据 sigma 来计算合适的 kernel_size（依据 3 sigma 原则）
                                            默认为 None
                sigma:                  <float> 强度
        """
        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        assert isinstance(image, np.ndarray) and image.ndim == 3
        if sigma == 0:
            res = image
        else:
            if kernel_size is None:
                kernel_size = 2 * math.ceil(3 * sigma) + 1
            if not isinstance(kernel_size, (list, tuple,)):
                kernel_size = [kernel_size, kernel_size]
            upper_kz = max(image.shape[0:2]) // 2 + 1
            for i, kz in enumerate(kernel_size):
                assert kz > 0 and kz % 2 == 1, \
                    f'kernel_size should be positive odd integer, but got an {kz}'
                kz = min(upper_kz, int(kz))
                kernel_size[i] = kz

            res = cv2.GaussianBlur(src=image, ksize=kernel_size, sigmaX=sigma)

        input_s["image"] = res

        # 补充详细信息
        input_s["details"] = dict(kernel_size=kernel_size)  # 实际使用的 kernel_size

        return input_s


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format

    image = Image.open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "test_data/data_0/",
                     "ILSVRC2012_val_00038993.JPEG"))
    image.show()

    sigma = 1

    #
    output_s = TRANSFORMS.get(name=":for_images:blur:Gaussian_Blur")(kernel_size=None, sigma=sigma,
                                                                     b_include_details=True)(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE).show()

    # 和 torchvision 比较
    output_s_2 = TRANSFORMS.get(name=":for_images:torchvision:GaussianBlur")(kernel_size=31, sigma=sigma)(
        input_s=dict(image=image)
    )
    convert_format(image=output_s_2["image"], output_format=Image_Format.PIL_IMAGE).show()

    diff = convert_format(image=output_s_2["image"], output_format=Image_Format.NP_ARRAY) - \
           convert_format(image=output_s["image"], output_format=Image_Format.NP_ARRAY)
    convert_format(image=diff, output_format=Image_Format.PIL_IMAGE).show()
    print(f'avg diff:{np.mean(diff)}')
