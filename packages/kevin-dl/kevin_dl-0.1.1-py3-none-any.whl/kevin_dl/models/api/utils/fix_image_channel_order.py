import os
import cv2


def fix_image_channel_order(image, b_bgr_raw=False, b_bgr_dst=False):
    if isinstance(image, (str,)):
        assert os.path.isfile(os.path.expanduser(image))
        image = cv2.imread(filename=os.path.expanduser(image))
        b_bgr_raw = True
    if b_bgr_raw and not b_bgr_dst:  # 输入是bgr 但是模型要求rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif not b_bgr_raw and b_bgr_dst:  # 输入是rgb 但是模型要求bgr
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image
