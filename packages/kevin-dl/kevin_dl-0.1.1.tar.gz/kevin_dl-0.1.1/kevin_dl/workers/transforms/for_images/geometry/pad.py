import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS
from kevin_dl.workers.transforms.for_images.geometry.utils import neaten_keypoints, neaten_bboxes, crop_bboxes, \
    crop_keypoints, neaten_padding, pad_image


@TRANSFORMS.register()
class Pad(Base_Transform):
    """
        在图像周围填充边界
            支持对图像以及对应的 bboxes, masks, key points 一同进行变换。
    """
    name = ":for_images:geometry:Pad"

    def cal(self, input_s, padding=None, fill=0, padding_mode="constant",
            padding_mode_for_mask=None, fill_for_mask=None,
            b_crop_bboxes=False, b_crop_keypoints=False, **kwargs):
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
            padding:            <int/tuple/list/dict> 填充边缘的大小
                                    如果提供的是单个整数，则用于填充所有边框。
                                    如果提供的是序列
                                        - 长度为 2，则分别用于填充左/右和上/下的边框。
                                        - 长度为 4，则分别用于填充左、上、右和下边框。
                                    如果提供的是字典，则需要输入形如 {"left":..., "top":..., "right":..., "bottom":...} 来指定四边的填充大小
                                        若其中某个键不指定，则默认该键对应的填充为 0.
            fill:               <int/tuple> constant 模式下的填充值
                                    默认为 0
            padding_mode:       <str> 对于缺失部分的填充模式
                                    目前支持以下选项：
                                        - "constant"
                                        - "edge"
                                        - "reflect"
                                        - "symmetric"
                                    默认为 "constant"
            padding_mode_for_mask:  <str> 对于 masks 部分的填充模式
            fill_for_mask:      <int/tuple> constant 模式下 masks 的填充值
                        以上两参数默认与 padding_mode 和 fill 相同。
            b_crop_bboxes:          <boolean> 是否对超出图像区域之外的 bboxes 进行裁剪。
                                        默认 False。
            b_crop_keypoints:       <boolean> 是否对超出图像区域之外的 关键点 进行裁剪。
                                        默认 False。

        返回：
            在 input_s 中新增填充后的 image/masks/bboxes/keypoints，并在 details 中记录参数
        """
        padding_mode_for_mask = padding_mode_for_mask or padding_mode
        fill_for_mask = fill_for_mask or fill
        left, top, right, bottom = neaten_padding(padding)

        # 处理图像
        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        img_h, img_w = image.shape[:2]
        image = pad_image(image, top, bottom, left, right, padding_mode, fill)
        new_h, new_w = image.shape[:2]
        input_s["image"] = image

        # 处理 masks
        if "masks" in input_s:
            input_s["masks"] = input_s["masks"] if isinstance(input_s["masks"], (list, tuple,)) else [input_s["masks"]]
            for i in range(len(input_s["masks"])):
                input_s["masks"][i] = pad_image(input_s["masks"][i], top, bottom, left, right, padding_mode_for_mask,
                                                fill_for_mask)

        # 处理 bboxes
        if "bboxes" in input_s:
            bboxes = neaten_bboxes(bboxes=input_s["bboxes"])
            # 添加左和上偏移
            bboxes[:, [0, 2]] += left  # x_min, x_max
            bboxes[:, [1, 3]] += top  # y_min, y_max
            input_s["bboxes"] = bboxes
            # 裁剪
            if b_crop_bboxes:
                input_s["bboxes"] = crop_bboxes(bboxes=input_s["bboxes"], img_hw=(new_h, new_w))

        # 处理 keypoints
        if "keypoints" in input_s:
            keypoints = neaten_keypoints(keypoints=input_s["keypoints"])
            keypoints[:, 0] += left  # x
            keypoints[:, 1] += top  # y
            input_s["keypoints"] = keypoints
            # 裁剪
            if b_crop_keypoints:
                input_s["keypoints"] = crop_keypoints(keypoints=input_s["keypoints"], img_hw=(new_h, new_w))

        # 记录 details
        input_s["details"] = dict(
            padding=(left, top, right, bottom), fill=fill, padding_mode=padding_mode,
            padding_mode_for_mask=padding_mode_for_mask, fill_for_mask=fill_for_mask,
            new_hw=(new_h, new_w), raw_hw=(img_h, img_w)
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
    transform = Pad(padding=(-100, -100, 50, 50), fill=(225, 0, 0), padding_mode="constant",
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
