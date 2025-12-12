import copy
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format


def build_transform_for_albumentations(registered_name, worker_builder, accepted_format=Image_Format.NP_ARRAY):
    """
        根据给定的 worker_builder 构建包含对应 worker 的一个 Transform 类
    """
    import albumentations as A

    class Transform_of_Given_Worker(Base_Transform):
        f"""
            根据给定的 worker_builder {worker_builder} 构建的 Transform 类，
                注册名称为 {registered_name}，构建脚本为 {__file__}
        """
        name = registered_name

        def cal(self, input_s, **kwargs):
            """
                参数：
                    input_s:                <dict>
                                                其中包含：
                                                    image:      <torch.tensor> shape [C, H, W]
                    ...                     用于构建 worker 的参数
            """
            input_s["image"] = convert_format(image=input_s["image"], output_format=accepted_format)

            if getattr(self, "worker", None) is None or len(self.random_item_s) > 0:
                kwargs = copy.deepcopy(kwargs)
                # 需要新建/重建 worker
                compose_settings = dict()
                if "bbox_params" in kwargs:
                    if "label_fields" not in kwargs["bbox_params"]:
                        setattr(self, "b_need_dummy_labels", True)
                        kwargs["bbox_params"]["label_fields"] = ["dummy_labels"]
                    compose_settings["bbox_params"] = A.BboxParams(**kwargs.pop("bbox_params"))
                if "keypoint_params" in kwargs:
                    compose_settings["keypoint_params"] = A.KeypointParams(**kwargs.pop("keypoint_params"))
                if compose_settings:
                    setattr(self, "worker", A.Compose(transforms=[worker_builder(**kwargs)], **compose_settings))
                else:
                    setattr(self, "worker", worker_builder(**kwargs))

            if getattr(self, "b_need_dummy_labels", False):
                input_s["dummy_labels"] = [0]
            res = self.worker(**input_s)
            if isinstance(res, dict):
                input_s.update(res)
            else:
                input_s["image"] = res

            return input_s

    # 使用 type() 动态创建 Transform_of_Given_Worker 的子类，这样才能保存到全局变量中
    cls = type(f'Transform_of_Given_Worker-{registered_name}', (Transform_of_Given_Worker,), {})

    return cls


if __name__ == '__main__':
    import os
    from PIL import Image
    import albumentations as A
    from kevin_dl.workers.transforms.for_images.utils import get_format
    from kevin_dl.utils.variable import root_dir
    from kevin_dl.workers.variable import TRANSFORMS

    # ---------------------- 数据准备 ---------------------- #

    image = Image.open(
        os.path.join(root_dir,
                     "kevin_dl/workers/transforms/for_images/test/test_data/data_0/ILSVRC2012_val_00040001.JPEG"))

    # ---------------------- 注册 ---------------------- #

    name_ = ":for_images:albumentations:Resize"

    ts = build_transform_for_albumentations(
        registered_name=name_, worker_builder=A.Resize
    )

    TRANSFORMS.add(obj=ts, b_execute_now=False)

    # ---------------------- 简单调用 ---------------------- #

    output_s = TRANSFORMS.get(name=name_)(height=224, width=224)(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()

    # ---------------------- 带bbox，关键点调用 ---------------------- #

    # 检测框格式： [x_min, y_min, x_max, y_max]（这里采用 pascal_voc 格式）
    bboxes = [[50, 60, 200, 300]]
    # 分类信息，对应每个框的类别标签
    category_ids = [1]
    # 关键点格式：[x, y]
    keypoints = [[100, 150]]

    output_s = TRANSFORMS.get(name=name_)(
        height=224, width=224,
        bbox_params=dict(format='pascal_voc', label_fields=['category_ids']),
        keypoint_params=dict(format='xy')
    )(
        input_s=dict(image=image, bboxes=bboxes, category_ids=category_ids, keypoints=keypoints)
    )

    from kevin_dl.tools.face.utils import plot_bbox_and_landmarks

    # 在原图上绘制检测框和关键点
    raw = convert_format(image=image, output_format=Image_Format.NP_ARRAY)
    raw = plot_bbox_and_landmarks(image=raw, bbox=bboxes[0], landmarks=keypoints, person_id=category_ids[0])
    raw = convert_format(image=raw, output_format=Image_Format.PIL_IMAGE)
    raw.show()

    # 在原图上绘制检测框和关键点
    out = convert_format(image=output_s["image"], output_format=Image_Format.NP_ARRAY)
    out = plot_bbox_and_landmarks(image=out, bbox=output_s["bboxes"][0], landmarks=output_s["keypoints"],
                                  person_id=output_s["category_ids"][0])
    out = convert_format(image=out, output_format=Image_Format.PIL_IMAGE)
    out.show()
