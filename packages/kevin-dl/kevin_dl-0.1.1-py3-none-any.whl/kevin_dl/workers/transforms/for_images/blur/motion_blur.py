import numpy as np
import cv2
import math
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class Motion_Blur(Base_Transform):
    """
        动态模糊
    """
    name = ":for_images:blur:Motion_Blur"

    def cal(self, input_s, kernel_size=10, angle=None, **kwargs):
        """
            参数：
                input_s:                <dict>
                                            其中包含：
                                                image:      <np.array> shape [H, W, C]
                kernel_size:            <int> 模糊矩阵的卷积核大小
                                            越大，模糊程度越高
                angle:                  <float> 沿哪个方向进行运动
                                            当设置为 None 时，将从 [0~180) 中任意取一整数
                                            默认为 None
        """
        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        assert image.ndim == 3
        kernel_size = int(kernel_size)
        if kernel_size <= 1:
            res = image
        else:
            if angle is None:
                angle = np.random.randint(0, 180)
            angle += 45

            # 生成模糊核
            motion_blur_kernel = np.diag(np.ones(kernel_size))
            # 沿 angle 方向旋转
            M = cv2.getRotationMatrix2D((kernel_size / 2, kernel_size / 2), angle, 1)
            motion_blur_kernel = cv2.warpAffine(motion_blur_kernel, M, (kernel_size, kernel_size))
            # 归一化
            motion_blur_kernel = motion_blur_kernel / kernel_size

            #
            res = cv2.filter2D(src=image, ddepth=-1, kernel=motion_blur_kernel)

        input_s["image"] = res

        return input_s


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format, Image_Format

    image = Image.open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "test_data", "ILSVRC2012_val_00038993.JPEG"))
    image.show()

    output_s = TRANSFORMS.get(name=":for_images:blur:Motion_Blur")(b_include_details=True, kernel_size=10)(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
