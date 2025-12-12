import os
import torch
import numpy as np
from kevin_dl.tools.face.utils import parse_landmarks
from kevin_dl.tools.variable import TOOLS


@TOOLS.register(name=":face:detect:SFD_Detector")
class SFD_Detector:
    """
        SFD ==> bbox; face_alignment ==> landmarks(68 pts)
    """

    def __init__(self, **kwargs):
        # 默认参数
        paras = {
            "b_use_gpu": torch.cuda.is_available()
        }
        # 获取参数
        paras.update(kwargs)

        try:
            import face_alignment
        except:
            raise ImportError('face_alignment is not installed, please install it by "pip install face_alignment"')
        hub_dir = os.path.join(os.path.dirname(__file__), "face_alignment_models")
        os.makedirs(hub_dir, exist_ok=True)
        torch.hub.set_dir(hub_dir)
        self.worker = face_alignment.FaceAlignment(
            landmarks_type=face_alignment.LandmarksType.TWO_D,
            device='cuda:0' if paras["b_use_gpu"] else 'cpu',
            flip_input=False, face_detector="sfd",
            **{k: v for k, v in paras.items() if k not in ["b_use_gpu", "face_detector"]})
        self.paras = paras

    def detect_face(self, image, **kwargs):
        """
            检出图片中的人脸框、关键点

            参数：
                image:          注意！！要求是 rgb 格式

            注意：返回的 score 是关键点评分的均值。
        """
        res = []
        ret = self.worker.get_landmarks(image, return_bboxes=True, return_landmark_score=True)
        if ret[0] is None:
            return res

        for landmarks, landmarks_scores, bbox in zip(*ret):
            res.append({'bbox': bbox[:4], 'landmarks': landmarks, 'score': np.mean(landmarks_scores)})

        # 按照人脸分数进行排序
        res.sort(key=lambda x: x['score'], reverse=True)

        return res

    def find_best_rotate_angle(self, image=None, detect_res_ls=None, **kwargs):
        """
            找出图像的最佳旋转角度
        """
        if detect_res_ls is None:
            detect_res_ls = self.detect_face(image=image)

        # 根据关键点（双眼中心和嘴角中心连线）计算出人脸角度
        if not kwargs.get("return_all_face", False):
            detect_res_ls.sort(key=lambda x: x['score'], reverse=True)
            detect_res_ls = detect_res_ls[:1]
        #
        res_ls = []
        for it in detect_res_ls:
            temp = parse_landmarks(landmarks=it["landmarks"], output_contents=["eyes_center", "mouth_center"],
                                   output_format="array")
            src = temp[1] - temp[0]
            tgt = np.array([0, 1])
            src = src / np.linalg.norm(src)
            tgt = tgt / np.linalg.norm(tgt)
            # 计算两个向量之间的夹角
            angle = np.degrees(np.arctan2(np.cross(src, tgt), np.dot(src, tgt)))
            res_ls.append(-angle % 360)
        #
        if kwargs.get("return_all_face", False):
            return res_ls
        else:
            return res_ls[0] if len(res_ls) > 0 else None


if __name__ == '__main__':
    from kevin_dl.tools.face.utils import rotate_image
    import cv2

    image = cv2.imread(
        "~/Desktop/gitlab_repos/kevin_dl/kevin_dl/tools/face/test/test_data/rotate/image_83.jpg")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    detector = SFD_Detector()
    angle = detector.find_best_rotate_angle(image=image)
    print(angle)

    res_image = rotate_image(image=image, angle=angle)
    cv2.imwrite(filename=os.path.join(
        "~/Desktop/gitlab_repos/kevin_dl/kevin_dl/tools/face/test/test_data/rotate/temp.jpg"),
        img=res_image)
