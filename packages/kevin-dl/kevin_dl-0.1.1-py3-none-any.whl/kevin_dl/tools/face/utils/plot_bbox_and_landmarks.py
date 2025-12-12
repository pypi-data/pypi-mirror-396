import cv2
import numpy as np


def plot_bbox_and_landmarks(image, bbox=None, landmarks=None, landmarks_names=None, person_id=None, b_inplace=True):
    """
        参数：
            bbox:           <list/array> [x_0, y_0, x_1, y_1]
    """
    if not b_inplace:
        image = image.copy()
    if landmarks is not None:
        if landmarks_names is None:
            landmarks_names = [f'{i}' for i in range(len(landmarks))]
        assert len(landmarks_names) == len(landmarks)

    if bbox is not None:
        bbox = np.asarray(bbox, dtype=int)
        cv2.rectangle(image, bbox[:2], bbox[-2:], (0, 255, 0), 2)
        if person_id is not None:
            cv2.putText(image, f'{person_id}', bbox[:2] - 10, cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if landmarks is not None:
        landmarks = np.asarray(landmarks, dtype=int)
        fontScale = 0.9 if len(landmarks) < 5 else 0.9 / np.log(len(landmarks)) * np.log(5)
        thickness = 2 if len(landmarks) < 5 else int(np.around(2 / np.log(len(landmarks)) * np.log(5)))
        for i, (x, y) in zip(landmarks_names, landmarks):
            cv2.circle(image, (x, y), 2, (255, 0, 0), -1)
            cv2.putText(image, f'{i}', (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=fontScale, color=(0, 0, 255), thickness=thickness)

    return image
