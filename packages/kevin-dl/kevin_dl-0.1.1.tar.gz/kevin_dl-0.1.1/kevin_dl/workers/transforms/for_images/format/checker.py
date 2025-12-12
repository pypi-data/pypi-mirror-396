import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import Image_Format, get_format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS
from kevin_dl.workers.transforms.for_images.geometry.utils import neaten_keypoints, neaten_bboxes


def check_shape(a, b):
    assert len(a) == len(b)
    for i, j in zip(a, b):
        assert i is None or j is None or i == j


@TRANSFORMS.register()
class Checker(Base_Transform):
    """
        对输入进行检查
            支持对图像以及对应的 bboxes, masks, key points 一同进行变换。
    """
    name = ":for_images:format:Checker"

    def cal(self, input_s, image_format=None, image_shape=None,
            bbox_nums=None, mask_nums=None, mask_shape=None,
            keypoint_nums=None, b_ignore_errors=False, **kwargs):
        """
        参数：
            input_s:            <dict> 输入。
                                    其中应该至少包含以下键值对：
                                        - image:            图像。
                                                                建议使用 np.array 输入，shape [H, W, C]
                                    可选的键值对有：
                                        - bboxes:           <list/array> 边界框列表。
                                                                每个框的格式为 (x_min, y_min, x_max, y_max)
                                                                其中 x 坐标：对应宽度（W）维度，表示水平方向的位置。
                                                                y 坐标：对应高度（H）维度，表示垂直方向的位置。
                                        - masks:            <list> 掩码图像 mask 列表。
                                        - keypoints:        <list/array> 关键点列表。
            image_format:       <Image_Format> 期望的图像格式
            image_shape:        <array> 期望的图像尺寸
                                    可以使用 None 表示不需检查的维度
                                    比如 [None, None, 3] 表示只要最后一个维度为 3 就视为满足条件。
            bbox_nums:          <int> 期望的 bbox 数量
            mask_nums:          <int> 期望的 mask 数量
            mask_shape:         <array/list of array> mask 应该满足的尺寸
                                    当其为单个尺寸时，表示所有 mask 的尺寸都应与此相同，
                                    当其为多个尺寸时，依次表示每个 mask 的期望尺寸。
            keypoint_nums:      <int> 期望的 keypoint 数量
                    当以上的参数设置为 None 时，表示不做检查。
            b_ignore_errors:    <boolean> 是否忽略报错。
                                    默认为 False，此时一旦检查不通过将会报错
        """
        b_pass_check = True
        try:
            # 检查图像
            if image_format is not None:
                assert get_format(image=input_s["image"]) is Image_Format(image_format)
            if image_shape is not None:
                check_shape(input_s["image"].shape, image_shape)

            # 检查 masks
            masks = input_s["masks"] if "masks" in input_s else None
            if mask_nums is not None:
                assert masks is not None and len(masks) == mask_nums
            if mask_shape is not None:
                mask_shape = np.asarray(mask_shape)
                if mask_shape.ndim == 1:
                    mask_shape = [mask_shape] * len(masks)
                for it, shape in zip(masks, mask_shape):
                    check_shape(it.shape, shape)

            # 检查 bboxes
            bboxes = neaten_bboxes(input_s["bboxes"]) if "bboxes" in input_s else None
            if bbox_nums is not None:
                assert bboxes is not None and len(bboxes) == bbox_nums

            # 处理 keypoints
            keypoints = neaten_keypoints(input_s["keypoints"]) if "keypoints" in input_s else None
            if keypoint_nums is not None:
                assert keypoints is not None and len(keypoints) == keypoint_nums
        except:
            b_pass_check = False

        if not b_ignore_errors and not b_pass_check:
            raise ValueError("check failed")

        # 记录 details
        input_s["details"] = dict(
            b_pass_check=b_pass_check
        )

        return input_s


if __name__ == "__main__":
    from kevin_dl.tools.face.utils import plot_bbox_and_landmarks

    # 构造一个示例 numpy 图像 (例如 300x400, 3 通道，BGR)
    image = np.full((400, 300, 3), 122, dtype=np.uint8)
    cv2.putText(image, "Test", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    #
    bboxes = [[50, 60, 200, 300], [100, 150, 250, 350]]
    mask = np.full((400, 300), 0, dtype=np.uint8)
    mask[:200, 100:250] = 255
    keypoints = [(60, 70, 114514), (120, 180, 1919810)]

    input_s_ = {
        "image": image,
        "bboxes": bboxes,
        "masks": [mask, mask],
        "keypoints": keypoints
    }

    # 实例化变换，比如将图像短边扩展到 150 像素
    transform = Checker(image_format="np.array", image_shape=(None, None, 3),
                        bbox_nums=2, mask_nums=2, mask_shape=(400, 300),
                        keypoint_nums=3, b_ignore_errors=True,
                        b_include_details=True)

    print(transform(input_s=input_s_))
