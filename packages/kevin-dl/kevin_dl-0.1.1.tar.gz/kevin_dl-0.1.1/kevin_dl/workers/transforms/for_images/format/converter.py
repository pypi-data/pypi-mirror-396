import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS


def check_shape(a, b):
    assert len(a) == len(b)
    for i, j in zip(a, b):
        assert i is None or j is None or i == j


@TRANSFORMS.register()
class Converter(Base_Transform):
    """
        对输入图片格式进行转换
    """
    name = ":for_images:format:Converter"

    def cal(self, input_s, output_format=None, **kwargs):
        """
        参数：
            input_s:            <dict> 输入。
                                    其中应该至少包含以下键值对：
                                        - image:            图像。
            output_format:      <Image_Format> 期望的图像格式
        """
        input_format = get_format(image=input_s["image"])
        input_s["image"] = convert_format(image=input_s["image"], output_format=output_format,
                                          input_format=input_format)

        # 记录 details
        input_s["details"] = dict(
            input_format=input_format.value,
            output_format=output_format
        )

        return input_s


if __name__ == "__main__":
    # 构造一个示例 numpy 图像 (例如 300x400, 3 通道，BGR)
    image = np.full((400, 300, 3), 122, dtype=np.uint8)
    cv2.putText(image, "Test", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    input_s_ = {
        "image": image
    }

    # 实例化变换，比如将图像短边扩展到 150 像素
    transform = Converter(output_format="torch.tensor", b_include_details=True)

    print(transform(input_s=input_s_))
