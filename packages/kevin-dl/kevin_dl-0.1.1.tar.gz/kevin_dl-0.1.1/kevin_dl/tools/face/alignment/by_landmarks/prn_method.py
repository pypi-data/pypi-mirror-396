import numpy as np
from kevin_dl.tools.face.alignment.utils import warp_affine_and_crop_by_point_pairs
from kevin_dl.tools.face.utils import perform_2d_affine_trans, parse_landmarks, cal_2d_affine_trans_matrix
from kevin_dl.tools.variable import TOOLS


@TOOLS.register(name=":face:alignment:by_landmarks:prn_method")
def prn_method(image, landmarks, desired_face_size=None, desired_image_size=None, padding_ls=None, **kwargs):
    landmarks = np.asarray(landmarks)
    assert len(landmarks) >= 68

    # 1. 旋转使得眼睛水平后，找出最左、左右关键点的中点。
    #   先旋转关键点
    eye_pts = parse_landmarks(landmarks=landmarks, output_contents=("left_eye", "right_eye"), output_format="array")
    tgt_pts = np.asarray([eye_pts[0], eye_pts[0]])
    tgt_pts[1, 0] += np.sqrt(np.sum(np.square(eye_pts[0] - eye_pts[1])))
    trans_mat = cal_2d_affine_trans_matrix(src=eye_pts, dst=tgt_pts, b_compact_form=False, b_return_error=False)
    landmarks_trans = perform_2d_affine_trans(trans_mat=trans_mat, points=landmarks)
    #   找出此时眼睛、嘴部关键点的中点
    centers = parse_landmarks(landmarks=landmarks_trans, output_contents=("eyes_center", "mouth_center"),
                              output_format="array")
    #   找出此时最左最右的关键点的中点
    chin_pts = parse_landmarks(landmarks=landmarks_trans, output_contents=("leftmost", "rightmost"),
                               output_format="array")
    centers = np.concatenate([centers, np.mean(chin_pts, axis=0, keepdims=True)], axis=0)

    # 2. 计算原始位置的坐标
    src_points = perform_2d_affine_trans(trans_mat=np.linalg.inv(trans_mat), points=centers)

    # 3. 计算目标位置的坐标
    dst_points = centers
    if dst_points[0, 1] > dst_points[1, 1]:  # 眼睛的y坐标比嘴巴的还大，说明人脸颠倒
        dst_points[..., 1] *= -1
    # 调整眼、嘴距离到 face_size 的35%
    temp = np.asarray(desired_face_size).reshape(-1)
    face_size_y, face_size_x = temp[-1], temp[0]
    dst_points *= (face_size_y * 0.35) / (dst_points[1, 1] - dst_points[0, 1])
    # 调整眼高
    dst_points[:, 1] -= dst_points[0, 1] - face_size_y * 0.3
    # 调整chin中点的左右位置
    dst_points[:, 0] -= dst_points[2, 0] - face_size_x * 0.5

    # 4. 进行仿射变换
    warped = warp_affine_and_crop_by_point_pairs(
        image=image, src_points=src_points, dst_points=dst_points,
        crop_ls=None, center_size=desired_face_size, padding_ls=padding_ls, desired_size=desired_image_size,
        **kwargs
    )
    return warped


if __name__ == '__main__':
    import os
    import cv2
    from kevin_toolbox.data_flow.file import json_
    from kevin_dl.tools.face.utils import plot_bbox_and_landmarks
    from kevin_dl.tools.face.detect import SFD_Detector

    data_dir = "~/Desktop/gitlab_repos/kevin_dl/kevin_dl/tools/face/test/test_data"
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    detector = SFD_Detector()
    for image_path in ["head_pose/pitch/30.png", "head_pose/yaw/30.png", "head_pose/yaw/90.png",
                       "head_pose/raw_face/0.png", "head_pose/roll/60.png", "examples_from_paper/prn_example_face.png"]:
        ori_image = cv2.cvtColor(cv2.imread(os.path.join(data_dir, image_path)), cv2.COLOR_BGR2RGB)
        res = detector.detect_face(image=ori_image)[0]
        ann_image = plot_bbox_and_landmarks(image=ori_image, landmarks=res["landmarks"], bbox=res["bbox"],
                                            b_inplace=False)
        #
        warped_image = prn_method(image=ann_image, landmarks=res["landmarks"],
                                  desired_face_size=140, desired_image_size=140, border_value=0.0)
        cv2.imwrite(os.path.join(output_dir, image_path.replace("/", "-")),
                    cv2.cvtColor(warped_image, cv2.COLOR_RGB2BGR))
