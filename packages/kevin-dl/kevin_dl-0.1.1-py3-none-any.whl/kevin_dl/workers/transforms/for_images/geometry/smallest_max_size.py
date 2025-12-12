import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS
from kevin_dl.workers.transforms.for_images.geometry.utils import neaten_keypoints, neaten_bboxes


def cal_scale(img_h, img_w, max_size=None):
    """
        根据 image 的尺寸计算缩放因子 scale
    """
    if max_size is None:
        return 1.0

    if not isinstance(max_size, (list, tuple,)):
        max_size = (max_size, max_size)
    assert len(max_size) == 2

    max_h, max_w = max_size
    if max_h is not None and max_w is not None:
        h_scale = max_h / img_h
        w_scale = max_w / img_w
        scale = max(h_scale, w_scale)
    elif max_h is not None:
        scale = max_h / img_h
    elif max_w is not None:
        scale = max_w / img_w
    else:
        # 如果两个均为 None，则不缩放
        scale = 1.0

    return scale


def convert_to_2_dim_array(x):
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[None, ...]
    return x


@TRANSFORMS.register()
class Smallest_Max_Size(Base_Transform):
    """
        将最短边缩放至指定大小
            支持对图像以及对应的 bboxes, masks, key points 一同进行缩放变换。
    """
    name = ":for_images:geometry:Smallest_Max_Size"

    def cal(self, input_s, max_size=None, interpolation=cv2.INTER_LINEAR,
            mask_interpolation=cv2.INTER_NEAREST, p=1.0, **kwargs):
        """
            参数：
                input_s:            <dict> 输入。
                                        其中应该至少包含以下键值对：
                                            - image:            图像。
                                                                    建议使用 np.array 输入，shape [H, W, C]
                                        可选的键值对有：
                                            - bboxes:           <list/array> 边界框列表。
                                                                    每个框的格式为 (x_min, y_min, x_max, y_max)
                                            - masks:            <list> 掩码图像 mask 列表。
                                            - keypoints:        <list/array> 关键点列表。
                                                                    每个关键点格式为 (x, y, ...)，后续部分可以携带其他属性。
                max_size:           <int/list of int> 指定 (目标高度, 目标宽度) 的最大约束。
                                        当输入的是整数时候，等效于 max_size=(max_size, max_size)
                                        当输入的是 tuple，其中第一、二个元素分别表示 (目标高度, 目标宽度)的最大约束，
                                        若元素为 None，则表示该维度不作约束。
                interpolation:      <str/int> 用于图像的插值方法。
                                        例如 cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_CUBIC, cv2.INTER_AREA, cv2.INTER_LANCZOS4 等
                                        默认 cv2.INTER_LINEAR。
                mask_interpolation: <str> 用于 mask 的插值方法。
                                        默认 cv2.INTER_NEAREST。
        """
        if self.rng.random() > p:
            return input_s

        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        img_h, img_w = image.shape[:2]
        scale = cal_scale(img_h=img_h, img_w=img_w, max_size=max_size)
        if abs(scale - 1.0) < 1e-10:
            return input_s
        new_h, new_w = int(round(img_h * scale)), int(round(img_w * scale))

        # 处理 image
        #   注意 cv2.resize 的 size 参数顺序为 (width, height)
        input_s["image"] = cv2.resize(image, (new_w, new_h), interpolation=interpolation)

        # 处理 masks
        if "masks" in input_s:
            input_s["masks"] = input_s["masks"] if isinstance(input_s["masks"], (list, tuple,)) else [input_s["masks"]]
            for i in range(len(input_s["masks"])):
                input_s["masks"][i] = cv2.resize(input_s["masks"][i], (new_w, new_h),
                                                 interpolation=mask_interpolation)

        # 处理 bboxes
        if "bboxes" in input_s:
            input_s["bboxes"] = neaten_bboxes(bboxes=input_s["bboxes"])
            input_s["bboxes"][:, :4] *= scale

        # 处理 keypoints
        if "keypoints" in input_s:
            input_s["keypoints"] = neaten_keypoints(keypoints=input_s["keypoints"])
            input_s["keypoints"][:, :2] *= scale

        # 补充详细信息
        input_s["details"] = dict(scale=scale, new_hw=(new_h, new_w), raw_hw=(img_h, img_w))

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
    transform = Smallest_Max_Size(max_size=150, b_include_details=True)

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
