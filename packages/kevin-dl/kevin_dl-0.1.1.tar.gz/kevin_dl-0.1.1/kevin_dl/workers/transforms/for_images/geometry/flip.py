import numpy as np
import cv2
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS
from kevin_dl.workers.transforms.for_images.geometry.utils import neaten_keypoints, neaten_bboxes

# 对于水平翻转（左右翻转），使用 cv2.flip(image, 1)；
#   如果需要垂直翻转，则使用 cv2.flip(image, 0)；
#   如果想要对图像同时做水平和垂直翻转，则使用 cv2.flip(image, -1)。
# flip_code_s: {(<b_horizontal_flip>, <b_vertical_flip>): <int>, ...}
flip_code_s = {(True, True): -1, (True, False): 1, (False, False): None, (False, True): 0}


def flip_bboxes(bboxes, img_hw, flip_code):
    img_h, img_w = img_hw
    if flip_code == 1 or flip_code == -1:
        # 水平翻转，改变 x 坐标
        #   new_x_min = w - x_max, new_x_max = w - x_min
        bboxes[:, 0], bboxes[:, 2] = img_w - bboxes[:, 2], img_w - bboxes[:, 0]
    if flip_code == 0 or flip_code == -1:
        # 垂直翻转，改变 y 坐标
        #   new_y_min = h - y_max, new_y_max = h - y_min
        bboxes[:, 1], bboxes[:, 3] = img_h - bboxes[:, 3], img_h - bboxes[:, 1]
    return bboxes


def flip_keypoints(keypoints, img_hw, flip_code):
    img_h, img_w = img_hw
    if flip_code == 1 or flip_code == -1:
        # 水平翻转，改变 x 坐标
        keypoints[:, 0] = img_w - keypoints[:, 0]  # new_x = w - x
    if flip_code == 0 or flip_code == -1:
        # 垂直翻转，改变 y 坐标
        keypoints[:, 1] = img_h - keypoints[:, 1]  # new_y = h - y
    return keypoints


@TRANSFORMS.register()
class Flip(Base_Transform):
    """
        沿着X轴或者Y轴方向上的中心线翻转
            支持对图像以及对应的 bboxes, masks, key points 一同进行缩放变换。
    """
    name = ":for_images:geometry:Flip"

    def cal(self, input_s, p_horizontal=0.0, p_vertical=0.0, **kwargs):
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
                p_horizontal:       <float> 水平翻转的概率。
                p_vertical:         <float> 垂直翻转的概率。
        """
        b_horizontal_flip, b_vertical_flip = self.rng.random() <= p_horizontal, self.rng.random() <= p_vertical
        flip_code = flip_code_s[(b_horizontal_flip, b_vertical_flip)]
        if flip_code is None:
            return input_s

        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        img_h, img_w = image.shape[:2]

        # 处理图像
        image = cv2.flip(image, flip_code)
        input_s["image"] = image

        # 处理 masks
        if "masks" in input_s:
            input_s["masks"] = input_s["masks"] if isinstance(input_s["masks"], (list, tuple,)) else [input_s["masks"]]
            for i in range(len(input_s["masks"])):
                input_s["masks"][i] = cv2.flip(input_s["masks"][i], flip_code)

        # 处理 bboxes
        if "bboxes" in input_s:
            input_s["bboxes"] = neaten_bboxes(bboxes=input_s["bboxes"])
            input_s["bboxes"] = flip_bboxes(bboxes=input_s["bboxes"], img_hw=(img_h, img_w), flip_code=flip_code)

        # 处理 keypoints
        if "keypoints" in input_s:
            input_s["keypoints"] = neaten_keypoints(keypoints=input_s["keypoints"])
            input_s["keypoints"] = flip_keypoints(keypoints=input_s["keypoints"], img_hw=(img_h, img_w),
                                                  flip_code=flip_code)

        # 补充详细信息
        input_s["details"] = dict(
            b_horizontal_flip=b_horizontal_flip, b_vertical_flip=b_vertical_flip, flip_code=flip_code
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
    transform = Flip(p_horizontal=1.0, p_vertical=1.0)

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
