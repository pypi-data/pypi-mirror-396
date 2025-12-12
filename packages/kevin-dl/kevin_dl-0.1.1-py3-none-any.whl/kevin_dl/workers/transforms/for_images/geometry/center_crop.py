import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.transforms.for_images.geometry.utils import neaten_keypoints, neaten_bboxes, neaten_crop_size, \
    crop_bboxes, crop_keypoints, pad_if_needed
from kevin_dl.workers.variable import TRANSFORMS


def get_crop_coords(img_hw, dst_hw):
    """
        根据图像的尺寸计算中心裁剪区域的坐标 (x1, y1, x2, y2)。
    """
    img_h, img_w = img_hw
    dst_h, dst_w = dst_hw
    y1 = max(0, (img_h - dst_h) // 2)
    x1 = max(0, (img_w - dst_w) // 2)
    y2 = y1 + dst_h
    x2 = x1 + dst_w
    return x1, y1, x2, y2


@TRANSFORMS.register()
class Center_Crop(Base_Transform):
    """
        中心裁切
            支持对图像以及对应的 bboxes, masks, key points 一同进行缩放变换。
    """
    name = ":for_images:geometry:Center_Crop"

    def cal(self, input_s, size=None, b_pad_if_needed=False,
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
        img_h, img_w = image.shape[:2]
        new_h, new_w = neaten_crop_size(size=size, img_hw=(img_h, img_w), b_pad_if_needed=b_pad_if_needed)
        if new_h == img_h and new_w == img_w:
            return input_s
        crop_x1, crop_y1, crop_x2, crop_y2 = get_crop_coords(img_hw=(img_h, img_w), dst_hw=(new_h, new_w))

        # 处理图像
        image, (pad_y1, pad_x1, pad_y2, pad_x2) = pad_if_needed(image=image, dst_hw=(new_h, new_w),
                                                                border_mode=border_mode, fill=fill)
        input_s["image"] = image[crop_y1:crop_y2, crop_x1:crop_x2]

        # 处理 masks
        if "masks" in input_s:
            input_s["masks"] = input_s["masks"] if isinstance(input_s["masks"], (list, tuple)) else [input_s["masks"]]
            for i in range(len(input_s["masks"])):
                m, _ = pad_if_needed(image=input_s["masks"][i], dst_hw=(new_h, new_w),
                                     border_mode=border_mode, fill=fill)
                input_s["masks"][i] = m[crop_y1:crop_y2, crop_x1:crop_x2]

        # 处理 bboxes
        if "bboxes" in input_s:
            input_s["bboxes"] = neaten_bboxes(bboxes=input_s["bboxes"])
            input_s["bboxes"][:, :4] += np.asarray([pad_x1 - crop_x1, pad_y1 - crop_y1,
                                                    pad_x1 - crop_x1, pad_y1 - crop_y1])[None, ...]
            # 裁剪
            if b_crop_bboxes:
                input_s["bboxes"] = crop_bboxes(bboxes=input_s["bboxes"], img_hw=(new_h, new_w))

        # 处理 keypoints
        if "keypoints" in input_s:
            input_s["keypoints"] = neaten_keypoints(keypoints=input_s["keypoints"])
            input_s["keypoints"][:, :2] += np.asarray([pad_x1 - crop_x1, pad_y1 - crop_y1])[None, ...]
            # 裁剪
            if b_crop_keypoints:
                input_s["keypoints"] = crop_keypoints(keypoints=input_s["keypoints"], img_hw=(new_h, new_w))

        # 补充详细信息
        input_s["details"] = dict(
            pad_ls=(pad_x1, pad_y1, pad_x2, pad_y2),
            crop_ls=(crop_x1, crop_y1, crop_x2, crop_y2), new_hw=(new_h, new_w),
            raw_hw=(img_h, img_w)
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
    transform = Center_Crop(size=(150, 250), b_include_details=True, b_pad_if_needed=True, fill=255,
                            b_crop_bboxes=True, b_crop_keypoints=True)

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
