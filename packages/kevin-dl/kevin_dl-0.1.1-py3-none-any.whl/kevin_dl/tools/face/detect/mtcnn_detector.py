import os
import torch
import copy
import numpy as np
from kevin_dl.tools.face.utils import gaussian_filter_1d, rotate_image
from kevin_dl.tools.variable import TOOLS


@TOOLS.register(name=":face:detect:MTCNN_Detector")
class MTCNN_Detector:
    """
        MTCNN ==> bbox; landmarks(5 pts)
    """

    def __init__(self, **kwargs):
        # 默认参数
        paras = {
            "b_use_gpu": torch.cuda.is_available(),
            "thresholds": [0.4, 0.6, 0.6]
        }
        # 获取参数
        paras.update(kwargs)

        try:
            from facenet_pytorch import MTCNN
        except:
            raise ImportError('facenet_pytorch is not installed, please install it by "pip install facenet_pytorch"')
        self.worker = MTCNN(keep_all=True, device=torch.device('cuda:0' if paras["b_use_gpu"] else 'cpu'),
                            **{k: v for k, v in paras.items() if k not in ["b_use_gpu", ]})
        self.paras = paras

    def detect_face(self, image, **kwargs):
        """
            检出图片中的人脸框、关键点

            参数：
                image:          注意！！要求是 rgb 格式
        """

        # 检测人脸，获取人脸框和关键点
        boxes, probs, points = self.worker.detect(img=image, landmarks=True)
        boxes = [] if boxes is None else boxes

        res = [{'bbox': boxes[i].astype(dtype=float), 'landmarks': points[i].astype(dtype=float),
                'score': probs[i]} for i in range(len(boxes))]
        # 按照人脸分数进行排序
        res.sort(key=lambda x: x['score'], reverse=True)

        return res

    def find_best_rotate_angle(self, image, **kwargs):
        """
            找出图像的最佳旋转角度
        """
        known_res_s = dict()
        base_angles = None
        for range_, step, b_get_fine_angle in [
            ((-180, 180), 45, False),
            ((-45, 45), 15, False),
            ((-15, 15), 5, False),
            ((-5, 5), 1, True)
        ]:
            best_angle, res_s = self.evaluate_scores_at_diff_rotate_angles(
                image=image, base_angles=base_angles, step=step, range_=range_,
                decimals=1, b_get_fine_angle=b_get_fine_angle, known_res_s=known_res_s
            )
            base_angles = np.arange(*range_, step) if best_angle is None else [best_angle]
            known_res_s.update(res_s)

        return best_angle

    def evaluate_scores_at_diff_rotate_angles(self, image, step, range_, base_angles=None, known_res_s=None, decimals=1,
                                              b_get_fine_angle=False):
        """
            在不同角度下获取最佳人脸分数

            参数：
                base_angles:        <list of angle>
                step:               <float>
                range_:             [st, ed]
                        将依次以 base_angles 中的每个 base_angle 角度为中心，按照step的步长，在base_angle+range_[0]到range_+range[1]的范围内，
                        检测图像，并返回最高得分的旋转角度。包头包尾。
                known_res_s:        <dict> 已有的结果
                                    结构为：
                                    {
                                        <angle>:{
                                            "score": <float>,
                                            ...
                                        }
                                    }
                                    若需要检测的角度在 known_res_s 中已经存在，则直接返回其中的结果，实现加速。
                decimals:           <int> 角度值的精度（保留多少位小数）
                b_get_fine_angle:   <boolean> 是否通过高斯平滑，获取精细角度
        """
        known_res_s = dict() if known_res_s is None else known_res_s
        base_angles = [0] if base_angles is None else base_angles
        assert range_[0] <= range_[1]

        # 获取各个角度下的检测分数
        res_s = dict()
        for base_angle in base_angles:
            for angle in np.arange(base_angle + range_[0], base_angle + range_[1] + 10 ** (-decimals) / 2, step):
                angle = np.around(angle % 360, decimals=decimals)
                if angle in known_res_s:
                    res_s[angle] = known_res_s[angle]
                    continue
                if angle in res_s:
                    continue
                #
                temp_ls = self.detect_face(image=rotate_image(image=image, angle=angle))
                if len(temp_ls) == 0:
                    res_s[angle] = dict(score=None)
                else:
                    res_s[angle] = copy.deepcopy(temp_ls[0])
                    res_s[angle]["detect_res"] = temp_ls

        # 计算最佳角度
        scores = [(k, v["score"]) for k, v in res_s.items() if v["score"] is not None]
        if len(scores) == 0:
            best_angle = None
        else:
            if not b_get_fine_angle:
                # 取分数最大的角度
                best_angle = max(scores, key=lambda x: x[1])[0]
            else:
                # 进行高斯平滑，然后取最值
                X, Y = gaussian_filter_1d(x_ls=[i[0] for i in scores],
                                          y_ls=[i[1] for i in scores],
                                          sigma=step, decimals=decimals)
                best_angle = np.around(X[np.argmax(Y)], decimals=decimals)

        return best_angle, res_s
