import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms.for_images.patch.utils import select_and_paste_patch
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class Select_and_Paste_Patch(Base_Transform):
    """
        将原图中指定位置的多个 patch 粘贴到新图指定的位置上
    """
    name = ":for_images:patch:Select_and_Paste_Patch"

    def cal(self, input_s, desired_size=None, default_value=0, **kwargs):
        f"""
            参数：
                input_s:                <dict>
                                            其中包含：
                                                image:      <np.array> shape [H, W, C]
                desired_size:           <int/list of integers> 新图的长和宽
                                            默认为 None，此时将使用原图的长和宽作为新图的长和宽
                default_value:          <int/float> 新图中的默认值
                                            默认为 0
                                            当设置为 None 时，将使用原图的缩放结果作为新图的默认值
            其余参数同 select_and_paste_patch()，包括：
                src_bbox_ls:
                src_bbox_type:
                dst_bbox_ls:
                dst_bbox_type:
        """
        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        assert isinstance(image, np.ndarray) and image.ndim == 3
        if desired_size is None:
            desired_size = image.shape[0:2]
        if isinstance(desired_size, int):
            desired_size = [desired_size] * 2

        if default_value is None:
            dst_image = cv2.resize(image, desired_size)
        else:
            dst_image = np.ones(list(desired_size)+[image.shape[-1]], dtype=image.dtype) * default_value
        dst_image = select_and_paste_patch(src_image=image, dst_image=dst_image, **kwargs)

        input_s["image"] = dst_image

        # 补充详细信息
        input_s["details"] = dict(desired_size=desired_size, default_value=default_value, **kwargs)

        return input_s


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format

    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "test_data", "data_1")
    image = Image.open(os.path.join(data_dir, "Tadokor_Koji_the_Japanese_representative.jpg"))

    desired_size = 224
    src_bbox_ls, dst_bbox_ls = [], []
    for i in range(4):
        for j in range(4):
            src_bbox_ls.append([i / 4 + 1 / 8, j / 4 + 1 / 8, desired_size // 4, desired_size // 4])
            dst_bbox_ls.append([i / 4 + 1 / 8, j / 4 + 1 / 8, 1 / 4, 1 / 4])

    output_s = TRANSFORMS.get(name=":for_images:patch:Select_and_Paste_Patch")(
        b_include_details=True, desired_size=desired_size, default_value=0,
        src_bbox_ls=src_bbox_ls, src_bbox_type="center-wh",
        dst_bbox_ls=dst_bbox_ls, dst_bbox_type="center-wh"
    )(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
