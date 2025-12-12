import cv2


def rotate_image(image, angle, flags=cv2.INTER_LINEAR, border_mode=cv2.BORDER_CONSTANT, border_value=0,
                 b_return_rotate_matrix=False):
    angle = angle % 360
    if angle == 0:
        return image
    # 获取图像的宽度和高度
    height, width = image.shape[:2]
    # 计算旋转中心点
    center = (width / 2, height / 2)
    # 执行旋转
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 计算旋转后的图像尺寸
    abs_cos = abs(rotation_matrix[0, 0])
    abs_sin = abs(rotation_matrix[0, 1])
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # 调整旋转矩阵以确保图像完全包含在内
    rotation_matrix[0, 2] += bound_w / 2 - center[0]
    rotation_matrix[1, 2] += bound_h / 2 - center[1]
    #
    rotated_image = cv2.warpAffine(image, rotation_matrix, (bound_w, bound_h), flags=flags,
                                   borderMode=border_mode, borderValue=border_value)
    if b_return_rotate_matrix:
        return rotated_image, rotation_matrix
    else:
        return rotated_image


if __name__ == '__main__':
    image_path = "~/Desktop/gitlab_repos/kevin_dl/kevin_dl/tools/face/test/test_data/head_pose/raw_face/0.png"
    ori_image = cv2.imread(image_path)
    rotated_image = rotate_image(ori_image, 90)
    cv2.imwrite(image_path + "_rotated.png", rotated_image)
