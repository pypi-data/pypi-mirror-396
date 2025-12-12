from kevin_dl.workers.transforms.for_images.geometry.utils import pad_image


def pad_if_needed(image, dst_hw, border_mode, fill):
    """
        如果图像尺寸小于目标尺寸，则进行填充。
    """
    img_h, img_w = image.shape[:2]
    dst_h, dst_w = dst_hw
    pad_top, pad_bottom, pad_left, pad_right = 0, 0, 0, 0

    if img_h < dst_h:
        diff = dst_h - img_h
        pad_top = diff // 2
        pad_bottom = diff - pad_top
    if img_w < dst_w:
        diff = dst_w - img_w
        pad_left = diff // 2
        pad_right = diff - pad_left

    if pad_top or pad_bottom or pad_left or pad_right:
        image = pad_image(image, pad_top, pad_bottom, pad_left, pad_right, border_mode, fill=fill)
    return image, (pad_top, pad_left, pad_bottom, pad_right)
