import numpy as np
import cv2
import math
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class Brightness_Shift(Base_Transform):
    """
        亮度调节
            注意：根据hls和rgb颜色空间的转换关系，亮度分量l和channel的顺序无关，所以本函数同时适用于 "BGR" 和 "RGB" 格式的图像
    """
    name = ":for_images:color:Brightness_Shift"

    def cal(self, input_s, keep_ratio=1.0, alpha=0, beta=0.2, **kwargs):
        """
            参数：
                input_s:                <dict>
                                            其中包含：
                                                image:      <np.array> shape [H, W, C]
                keep_ratio:             <float 0~1> 原图像亮度保留比例
                alpha:                  <float 0~1>
                beta:                   <float -1~1>
                    亮度调整关系式：
                        l_new = l_old * keep_ratio + (1-keep_ratio) * alpha + beta
                        l_new = min(max(l_new, 0), 1)
        """
        for i in (keep_ratio, alpha):
            assert isinstance(i, (float, int,)) and 0 <= i <= 1
        assert isinstance(beta, (float, int,)) and -1 <= beta <= 1

        #
        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY).astype(dtype=np.float32)
        if np.max(image) > 1:
            image = np.clip(image / 255, 0, 1)

        # 将图像转换为HSV颜色空间
        res = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
        # 在 OpenCV 中 HLS 三个分量的范围为：
        #   H 是色相（0 到 360 度之间的角度值）
        #   L 是亮度（0 到 1 之间的值）
        #   S 是饱和度（0 到 1 之间的值）

        # 调整亮度
        temp = np.clip(res[..., 1] * keep_ratio + (1 - keep_ratio) * alpha + beta, 0, 1)
        # 统计亮度信息
        if self.b_include_details:
            # 统计亮度信息
            input_s["details"] = dict(
                brightness_before={k: eval(f'np.{k}(var)', {"var": res[..., 1], "np": np}) for k in ("median", "mean")},
                brightness_after={k: eval(f'np.{k}(var)', {"var": temp, "np": np}) for k in ("median", "mean")}
            )
        #
        res[..., 1] = temp

        # 转换原来的通道顺序
        res = cv2.cvtColor(res, cv2.COLOR_HLS2RGB)  # 同时也适配 BGR 格式图像

        # 将结果转换为 uint8 类型
        res = np.around(np.clip(res * 255, 0, 255)).astype(dtype=np.uint8)
        input_s["image"] = res

        return input_s


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format, Image_Format

    image = Image.open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "test_data", "ILSVRC2012_val_00038993.JPEG"))
    image.show()

    output_s = TRANSFORMS.get(name=":for_images:color:Brightness_Shift")(keep_ratio=0.5, alpha=0.5, beta=0.2,
                                                                         b_include_details=True)(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
