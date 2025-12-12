def crop_keypoints(keypoints, img_hw):
    h_, w_ = img_hw
    temp = (0 <= keypoints[:, 0]) * (keypoints[:, 0] <= w_) * (
            0 <= keypoints[:, 1]) * (keypoints[:, 1] <= h_)
    keypoints = keypoints[temp]
    return keypoints
