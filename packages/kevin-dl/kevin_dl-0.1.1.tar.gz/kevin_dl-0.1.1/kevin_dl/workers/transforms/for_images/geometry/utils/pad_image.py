import numpy as np
import cv2

# padding_mode 到 cv2 border type 的映射
_PADDING_MODE_MAP = {
    "constant": cv2.BORDER_CONSTANT,
    "edge": cv2.BORDER_REPLICATE,
    "reflect": cv2.BORDER_REFLECT,
    "symmetric": cv2.BORDER_REFLECT_101,
}


def pad_image(image, top, bottom, left, right, border_mode, fill):
    if image.ndim >= 3 and not isinstance(fill, (list, tuple)):
        img_c = image.shape[-1]
        fill = [fill] * img_c
    border_mode = _PADDING_MODE_MAP.get(border_mode, border_mode)
    img_h, img_w = image.shape[:2]

    # 裁切
    x1, y1 = max(0, -left), max(0, -top)
    x2, y2 = img_w - max(0, -right), img_h - max(0, -bottom)
    image = image[y1:max(y1, y2), x1:max(x1, x2)]

    # 填充
    #   cv2.copyMakeBorder 参数顺序：上，下，左，右
    out = cv2.copyMakeBorder(
        image, max(0, top), max(0, bottom), max(0, left), max(0, right),
        borderType=border_mode, value=fill
    )
    if len(out.shape) < len(image.shape):
        out = out[:, :, np.newaxis]
    return out
