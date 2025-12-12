import cv2
import numpy as np
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.transforms.for_images.geometry.utils import neaten_keypoints, neaten_bboxes, crop_bboxes, \
    crop_keypoints
from kevin_dl.tools.face.utils import perform_2d_affine_trans
from kevin_dl.workers.variable import TRANSFORMS


@TRANSFORMS.register()
class Rotation(Base_Transform):
    """
        随机旋转
    """
    name = ":for_images:geometry:Rotation"

    def cal(self, input_s, p=1.0, limits=None, option_ls=None, b_expand=True,
            interpolation=cv2.INTER_LINEAR, fill=0.0, center=None,
            b_crop_bboxes=False, b_crop_keypoints=False, **kwargs):
        """
            参数：
                input_s:                <dict> 输入。
                                            其中应该至少包含以下键值对：
                                                - image:            图像。
                                                                        建议使用 np.array 输入，shape [H, W, C]
                                            可选的键值对有：
                                                - bboxes:           <list/array> 边界框列表。
                                                                        每个框的格式为 (x_min, y_min, x_max, y_max)
                                                - masks:            <list> 掩码图像 mask 列表。
                                                - keypoints:        <list/array> 关键点列表。
                                                                        每个关键点格式为 (x, y, ...)，后续部分可以携带其他属性。
                p:                      <float> 进行旋转的概率。
                                            默认为 1.0
                limits:                 <tuple/list of int or float> 旋转范围（度）
                                            形如 (min, max) 的列表
                option_ls:              <tuple/list of int or float> 可选的角度（度）
                                以上两参数仅需指定一个即可，同时指定时以前者为准。
                b_expand:               <boolean> 是否扩展画布以包含整个旋转后图像
                                            默认为 True
                interpolation:          <str/int> 用于图像的插值方法。
                                            例如 cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_CUBIC, cv2.INTER_AREA, cv2.INTER_LANCZOS4 等
                                            默认 cv2.INTER_LINEAR。
                fill:                   <float> 填充值。
                                            可是单个数或 (B, G, R) 三元组
                center:                 <tuple/list of int or float> 旋转中心
                                            形如 (x, y)，当元素为 int 时，表示像素值，为 float 时表示相对值。
                                            默认为 None，表示图像中心。
                b_crop_bboxes:          <boolean> 是否对超出图像区域之外的 bboxes 进行裁剪。
                                            默认 False。
                b_crop_keypoints:       <boolean> 是否对超出图像区域之外的 关键点 进行裁剪。
                                            默认 False。
        """
        assert limits is not None or option_ls is not None

        if self.rng.random() > p:
            return input_s

        # 随机角度
        if limits is not None:
            if not isinstance(limits, (list, tuple)):
                limits = (limits, limits)
            assert len(limits) == 2
            angle = self.rng.uniform(limits[0], limits[1])
        else:
            angle = self.rng.choice(option_ls, size=1)[0]

        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        img_h, img_w = image.shape[:2]

        if angle == 0:
            input_s["image"] = image
            input_s["details"] = dict(angle=angle, new_hw=(img_h, img_w), raw_hw=(img_h, img_w))
            return input_s

        # 旋转中心点
        if center is None:
            cx, cy = img_w / 2.0, img_h / 2.0
        else:
            cx, cy = [i * j if isinstance(i, float) else i for i, j in zip(center, (img_w, img_h))]

        # 获取旋转矩阵
        M = cv2.getRotationMatrix2D((cx, cy), angle, scale=1.0)

        # 若需扩展画布，计算新尺寸并调整平移
        new_w, new_h = img_w, img_h
        if b_expand:
            corners = np.array([[0, 0, 1], [img_w, 0, 1], [img_w, img_h, 1], [0, img_h, 1]])
            pts = (M @ corners.T).T
            min_x, max_x = pts[:, 0].min(), pts[:, 0].max()
            min_y, max_y = pts[:, 1].min(), pts[:, 1].max()
            new_w = int(np.ceil(max_x - min_x))
            new_h = int(np.ceil(max_y - min_y))
            # 偏移
            M[0, 2] += -min_x
            M[1, 2] += -min_y

        # 处理 image
        #   仿射变换：rotate + translate + fill
        input_s["image"] = cv2.warpAffine(image, M, (new_w, new_h), flags=interpolation,
                                          borderMode=cv2.BORDER_CONSTANT,
                                          borderValue=fill)

        # 处理 masks
        if "masks" in input_s:
            input_s["masks"] = input_s["masks"] if isinstance(input_s["masks"], (list, tuple,)) else [input_s["masks"]]
            for i in range(len(input_s["masks"])):
                input_s["masks"][i] = cv2.warpAffine(input_s["masks"][i], M, (new_w, new_h), flags=interpolation,
                                                     borderMode=cv2.BORDER_CONSTANT,
                                                     borderValue=fill)

        # 处理 bboxes
        if "bboxes" in input_s:
            input_s["bboxes"] = neaten_bboxes(bboxes=input_s["bboxes"])
            temp = []
            for x_min, y_min, x_max, y_max in input_s["bboxes"][:, :4]:
                pts = np.array([[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]])
                pts_rot = perform_2d_affine_trans(trans_mat=M, points=pts)
                x_coords, y_coords = pts_rot[:, 0], pts_rot[:, 1]
                new_bbox = [x_coords.min(), y_coords.min(), x_coords.max(), y_coords.max()]
                temp.append(new_bbox)
            input_s["bboxes"][:, :4] = np.asarray(temp)
            # 裁剪
            if b_crop_bboxes:
                input_s["bboxes"] = crop_bboxes(bboxes=input_s["bboxes"], img_hw=(new_h, new_w))

        # 处理 keypoints
        if "keypoints" in input_s:
            input_s["keypoints"] = neaten_keypoints(keypoints=input_s["keypoints"])
            input_s["keypoints"][:, :2] = perform_2d_affine_trans(trans_mat=M, points=input_s["keypoints"][:, :2])
            # 裁剪
            if b_crop_keypoints:
                input_s["keypoints"] = crop_keypoints(keypoints=input_s["keypoints"], img_hw=(new_h, new_w))

        # 补充详细信息
        input_s["details"] = dict(angle=angle, new_hw=(new_h, new_w), raw_hw=(img_h, img_w))
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
    transform = Rotation(option_ls=(90, 90), b_expand=True, interpolation=cv2.INTER_NEAREST, center=None,
                         fill=(255, 255, 255), b_crop_bboxes=True, b_crop_keypoints=True)

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
