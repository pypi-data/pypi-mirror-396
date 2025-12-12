import torchvision.transforms as transforms
from kevin_dl.workers.transforms.for_images.utils import Image_Format, build_transform_of_worker

accepted_format_s = {
    "PILToTensor": Image_Format.PIL_IMAGE,
    "ToPILImage": (Image_Format.TORCH_TENSOR, Image_Format.NP_ARRAY),
    "ToTensor": (Image_Format.PIL_IMAGE, Image_Format.NP_ARRAY),
    "RandomHorizontalFlip": (Image_Format.TORCH_TENSOR, Image_Format.PIL_IMAGE),
}


def collect_from_torchvision():
    from kevin_dl.workers.variable import TRANSFORMS

    global accepted_format_s
    for k, v in transforms.__dict__.items():
        name = f':for_images:torchvision:{k}'
        if type(v) == type and TRANSFORMS.get(name=name, default=None) is None:
            if k in accepted_format_s:
                accepted_format = accepted_format_s[k]
            else:
                accepted_format = Image_Format.TORCH_TENSOR
            TRANSFORMS.add(obj=build_transform_of_worker.for_torchvision(
                registered_name=name, worker_builder=v, accepted_format=accepted_format
            ), b_execute_now=False)


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format, Image_Format
    from kevin_dl.workers.variable import TRANSFORMS
    import numpy as np
    import cv2
    import math

    image = Image.open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test/test_data/data_0",
                     "ILSVRC2012_val_00040001.JPEG"))

    collect_from_torchvision()

    output_s = TRANSFORMS.get(name=":for_images:torchvision:CenterCrop")(size=96)(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
