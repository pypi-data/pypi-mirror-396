import warnings
import inspect
from kevin_dl.workers.transforms.for_images.utils import Image_Format, build_transform_of_worker

accepted_format_s = {}

"""
albumentations 是一个非常流行且高效的图像增强库，专门针对计算机视觉任务设计。它内置了大量常用的增强操作，常见的操作包括：
    几何变换类：
        Resize：调整图像大小。
        RandomCrop / CenterCrop：随机或中心裁剪。
        HorizontalFlip / VerticalFlip：水平或垂直翻转。
        ShiftScaleRotate / RandomRotate90 / Transpose：平移、缩放、旋转以及90度旋转、转置等。
    颜色变换类：
        RandomBrightnessContrast：随机调整亮度和对比度。
        HueSaturationValue：调整色调、饱和度和明度。
        RGBShift、ChannelShuffle 等。
    噪声和模糊类：
        GaussNoise、MotionBlur、Blur、MedianBlur 等。
    形变类：
        ElasticTransform、GridDistortion、OpticalDistortion 等。

albumentations 的优势：
    支持对目标检测框、关键点、分割掩码等标注数据同步进行变换，保证数据的一致性。
    
更多信息可以参看：
    官网：https://albumentations.ai/docs/
    博客：https://zhuanlan.zhihu.com/p/371761014
"""


def collect_from_albumentations():
    from kevin_dl.workers.variable import TRANSFORMS
    import albumentations

    global accepted_format_s
    for k, v in albumentations.__dict__.items():
        name = f':for_images:albumentations:{k}'
        if callable(v) and inspect.isclass(v) and TRANSFORMS.get(name=name, default=None) is None:
            if k in accepted_format_s:
                accepted_format = accepted_format_s[k]
                if accepted_format != Image_Format.NP_ARRAY:
                    warnings.warn(f"albumentations requires that the input image must be a NumPy array")
            else:
                # albumentations 要求输入的图像必须为 NumPy 数组
                accepted_format = Image_Format.NP_ARRAY
            TRANSFORMS.add(obj=build_transform_of_worker.for_albumentations(
                registered_name=name, worker_builder=v, accepted_format=accepted_format
            ), b_execute_now=False)


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format
    from kevin_dl.workers.variable import TRANSFORMS

    image = Image.open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test/test_data/data_0",
                     "ILSVRC2012_val_00040001.JPEG"))

    collect_from_albumentations()

    output_s = TRANSFORMS.get(name=":for_images:albumentations:Resize")(height=96, width=96)(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
