import numpy as np
import cv2


def select_and_paste_patch(src_image, dst_image, src_bbox_ls, src_bbox_type, dst_bbox_ls, dst_bbox_type, **kwargs):
    f"""
        将 src_image 中指定的 patch 粘贴到 dst_image 指定的位置上
        
        参数：
            src_image:              <np.array> [H, W, c] 原始图像
            dst_image:              <np.array> [H, W, c] 目标图像
            src_bbox_ls:            <list of array> 原始图像中的区域序列
                                        当元素类型为 int 时，表示该 patch 的坐标
                                        当元素类型为 float 时，表示相对于图像的比例
            src_bbox_type:          <str or list of str> 原始图像中区域序列的格式
                                        当值为 str 时可选值：
                                            - "diagonals"：      任意两个对角点
                                            - "center-wh"：      中心点和宽高
                                            - "min-wh":         坐标最小角点和宽高
                                            - "max-wh":         坐标最大角点和宽高
                                        当值为 list of str 时，每个元素可选值同上，此时要求src_bbox_ls和dst_bbox_ls的元素个数相同
                                            一一对应。
            dst_bbox_ls:            <list of array> 目标图像中的区域序列
            dst_bbox_type:          <str> 目标图像中区域序列的格式
    """
    if isinstance(src_bbox_type, (str,)):
        src_bbox_type = [src_bbox_type] * len(src_bbox_ls)
    if isinstance(dst_bbox_type, (str,)):
        dst_bbox_type = [dst_bbox_type] * len(dst_bbox_ls)
    assert len(src_bbox_ls) == len(src_bbox_type) == len(dst_bbox_ls) == len(dst_bbox_type), \
        (f'mismatch between bbox_ls(src {len(src_bbox_ls)},dst{len(dst_bbox_ls)}) '
         f'and bbox_type(src {len(src_bbox_type)},dst{len(dst_bbox_type)})')

    for src_bbox, src_type, dst_bbox, dst_type in zip(src_bbox_ls, src_bbox_type, dst_bbox_ls, dst_bbox_type):
        x1, y1, x2, y2 = __parse_bbox(src_bbox, src_type, src_image.shape[0], src_image.shape[1])
        dx1, dy1, dx2, dy2 = __parse_bbox(dst_bbox, dst_type, dst_image.shape[0], dst_image.shape[1])
        # 将超出画幅的 src_bbox 进行裁剪，并同步修改 dst_bbox
        scale_x, scale_y = (dx1 - dx2) / (x2 - x1), (dy1 - dy2) / (y2 - y1)
        if x1 < 0:
            dx1 += int(x1 * scale_x)
            x1 = 0
        if y1 < 0:
            dy1 += int(y1 * scale_y)
            y1 = 0
        if x2 > src_image.shape[1]:
            dx2 -= int((src_image.shape[1] - x2) * scale_x)
            x2 = src_image.shape[1]
        if y2 > src_image.shape[0]:
            dy2 -= int((src_image.shape[0] - y2) * scale_y)
            y2 = src_image.shape[0]
        # 获取 patch
        patch = src_image[y1:y2, x1:x2]
        patch = cv2.resize(patch, (dx2 - dx1, dy2 - dy1))
        # 确保 patch 在 dst_image 中不会超出画幅
        patch = patch[
                max(0, -dy1):dst_image.shape[0] - dy2 if dy2 > dst_image.shape[0] else None,
                max(0, -dx1):dst_image.shape[1] - dx2 if dx2 > dst_image.shape[1] else None, ...]
        dx1, dy1, dx2, dy2 = max(0, dx1), max(0, dy1), min(dst_image.shape[1], dx2), min(dst_image.shape[0], dy2)
        # 将 patch 粘贴到 dst_image 中
        dst_image[dy1:dy2, dx1:dx2] = patch

    return dst_image


def __parse_bbox(bbox, bbox_type, image_height, image_width):
    temp = []
    for i, j in zip(bbox, [image_width, image_height, image_width, image_height]):
        temp.append(int(i * j) if isinstance(i, float) else i)
    bbox = temp

    # 解析源区域的坐标和尺寸
    if bbox_type == "diagonals":
        x1, y1, x2, y2 = bbox
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
    elif bbox_type == "center-wh":
        cx, cy, w, h = bbox
        x1, y1 = int(cx - w / 2), int(cy - h / 2)
        x2, y2 = int(cx + w / 2), int(cy + h / 2)
    elif bbox_type == "min-wh":
        x1, y1, w, h = bbox
        x2, y2 = x1 + w, y1 + h
    elif bbox_type == "max-wh":
        x2, y2, w, h = bbox
        x1, y1 = x2 - w, y2 - h
    else:
        raise ValueError(f"Unsupported bbox_type: {bbox_type}")

    return x1, y1, x2, y2


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test", "test_data", "data_1")
    image = Image.open(os.path.join(data_dir, "Tadokor_Koji_the_Japanese_representative.jpg"))

    image = convert_format(image=image, output_format=Image_Format.NP_ARRAY)
    dst_image = np.ones([150, 300, 3], dtype=image.dtype) * 127

    dst_image = select_and_paste_patch(
        src_image=image, dst_image=dst_image,
        src_bbox_ls=[
            [-0.1, -0.1, 1.1, 1.1],
            [144, 52, 294, 256],
            [144, 52, 294, 256]
        ],
        src_bbox_type=[
            "diagonals",
            "diagonals",
            "diagonals"
        ],
        dst_bbox_ls=[
            [0, 0, 0.25, 0.25],
            [1.2, 0, 0.5, 0.5],
            [0., 1.0, 0.5, 0.5]
        ],
        dst_bbox_type=[
            "diagonals",
            "diagonals",
            "diagonals"
        ]
    )
    dst_image = convert_format(image=dst_image, output_format=Image_Format.PIL_IMAGE)
    dst_image.show()
