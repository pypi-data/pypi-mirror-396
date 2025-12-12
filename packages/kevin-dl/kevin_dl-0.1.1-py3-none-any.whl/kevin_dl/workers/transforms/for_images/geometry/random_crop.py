import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.transforms.for_images.geometry.utils import neaten_keypoints, neaten_bboxes, neaten_crop_size, \
    crop_bboxes, crop_keypoints, pad_if_needed, neaten_padding, pad_image
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class Random_Crop(Base_Transform):
    """
        随机裁剪
            处理机制与 torchvision.transforms.RandomCrop 基本保持一致，参数的差异如下：
                - pad_if_needed ==> b_pad_if_needed
                - padding_mode ==> border_mode
            此外，当 b_pad_if_needed=False，且输入图像大小小于 size 时，并不会报错，而是不进行裁剪。
            支持对图像以及对应的 bboxes, masks, key points 一同进行随机裁剪。
    """
    name = ":for_images:geometry:Random_Crop"

    def cal(self, input_s, size=None, padding=None, b_pad_if_needed=False,
            b_crop_bboxes=False, b_crop_keypoints=False,
            border_mode=cv2.BORDER_CONSTANT, fill=0.0, **kwargs):
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
                                                                    每个关键点格式为 (x, y, ...)，后续部分可以携带其他属性。
                size:               <int/tuple of int or None> 裁剪后的图像大小。
                                        当输入的是整数时候，等效于 size=(size, size)
                                        当输入的是 tuple，其中第一、二个元素分别表示 (目标高度, 目标宽度)，
                                        若元素为 None，则表示使用原始图片的size，亦即该维度不做裁剪。
                padding:            <int or tuple or None> 先对图像进行多大的填充。
                b_pad_if_needed:    <boolean> 如果图像尺寸小于裁剪尺寸，是否进行填充
                                        默认 False。
                b_crop_bboxes:      <boolean> 是否对超出图像区域之外的 bboxes 进行裁剪。
                                        默认 False。
                b_crop_keypoints:   <boolean> 是否对超出图像区域之外的 关键点 进行裁剪。
                                        默认 False。
                border_mode:        <int> 填充边界的模式。
                                        默认 cv2.BORDER_CONSTANT。
                fill:               <float> 使用固定值填充时的具体数值。
                                        默认为 0.
        """
        assert isinstance(input_s, dict), "input_s should be a dict."
        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        padding = neaten_padding(padding)
        if size is None:
            size = image.shape[:2]

        # 先执行 padding
        if padding is not None:
            image = pad_image(image=image, top=padding[1], bottom=padding[3], left=padding[0], right=padding[2],
                              border_mode=border_mode, fill=fill)
        img_h, img_w = image.shape[:2]
        new_h, new_w = neaten_crop_size(size=size, img_hw=(img_h, img_w), b_pad_if_needed=b_pad_if_needed)

        image, (pad_y1, pad_x1, pad_y2, pad_x2) = pad_if_needed(image=image, dst_hw=(new_h, new_w),
                                                                border_mode=border_mode, fill=fill)

        # 随机选择裁剪坐标
        max_x = img_w - new_w
        max_y = img_h - new_h
        if max_x > 0:
            x1 = self.rng.randint(0, max_x)
        else:
            x1 = 0
        if max_y > 0:
            y1 = self.rng.randint(0, max_y)
        else:
            y1 = 0
        x2 = x1 + new_w
        y2 = y1 + new_h

        # 裁剪图像
        input_s["image"] = image[y1:y2, x1:x2]

        # 处理 masks
        if "masks" in input_s:
            input_s["masks"] = input_s["masks"] if isinstance(input_s["masks"], (list, tuple)) else [input_s["masks"]]
            for i in range(len(input_s["masks"])):
                m, _ = pad_if_needed(image=input_s["masks"][i], dst_hw=(new_h, new_w),
                                     border_mode=border_mode, fill=fill)
                input_s["masks"][i] = m[y1:y2, x1:x2]

        # 处理 bboxes
        if "bboxes" in input_s:
            input_s["bboxes"] = neaten_bboxes(bboxes=input_s["bboxes"])
            input_s["bboxes"][:, :4] += np.asarray([pad_x1 - x1, pad_y1 - y1,
                                                    pad_x1 - x1, pad_y1 - y1])[None, ...]
            if b_crop_bboxes:
                input_s["bboxes"] = crop_bboxes(bboxes=input_s["bboxes"], img_hw=(new_h, new_w))

        # 处理 keypoints
        if "keypoints" in input_s:
            input_s["keypoints"] = neaten_keypoints(keypoints=input_s["keypoints"])
            input_s["keypoints"][:, :2] += np.asarray([pad_x1 - x1, pad_y1 - y1])[None, ...]
            # 裁剪
            if b_crop_keypoints:
                input_s["keypoints"] = crop_keypoints(keypoints=input_s["keypoints"], img_hw=(new_h, new_w))

        # 补充详细信息
        input_s["details"] = dict(
            pad_ls=(pad_x1, pad_y1, pad_x2, pad_y2),
            crop_ls=(x1, y1, x2, y2), new_hw=(new_h, new_w), raw_hw=(img_h, img_w)
        )

        return input_s


if __name__ == '__main__':
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
    transform = Random_Crop(size=(400, 300), padding=10, b_pad_if_needed=True,
                            fill=255, b_crop_bboxes=True, b_crop_keypoints=True)

    out_s = transform(input_s=input_s_.copy())

    # shape
    for k in input_s_.keys():
        if k in ["details", "details_ls"]:
            continue
        elif k in ["masks", ]:
            for i, mask in enumerate(out_s[k]):
                print(f'for {k}[{i}]: raw: {input_s_[k][i].shape}, transformed: {mask.shape}')
        else:
            print(f'for {k}: raw: {np.asarray(input_s_[k]).shape}, transformed: {out_s[k].shape}')

    # details
    print(out_s["details"])

    # 可视化
    #   raw
    raw_image = input_s_["image"]
    raw_image = plot_bbox_and_landmarks(image=raw_image, bbox=None, landmarks=np.asarray(input_s_["keypoints"])[:, :2],
                                        b_inplace=False)
    for i in range(len(input_s_["bboxes"])):
        plot_bbox_and_landmarks(image=raw_image, bbox=input_s_["bboxes"][i], person_id=None, b_inplace=True)
    convert_format(image=raw_image, output_format=Image_Format.PIL_IMAGE).show()

    # res
    res_image = out_s["image"]
    res_image = plot_bbox_and_landmarks(image=res_image, bbox=None, landmarks=np.asarray(out_s["keypoints"])[:, :2],
                                        b_inplace=False)
    for i in range(len(out_s["bboxes"])):
        plot_bbox_and_landmarks(image=res_image, bbox=out_s["bboxes"][i], person_id=None, b_inplace=True)
    convert_format(image=res_image, output_format=Image_Format.PIL_IMAGE).show()
