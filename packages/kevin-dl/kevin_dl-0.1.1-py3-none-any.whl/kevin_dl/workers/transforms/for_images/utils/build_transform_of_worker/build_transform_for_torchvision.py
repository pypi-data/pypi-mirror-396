import re
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format


def build_transform_for_torchvision(registered_name, worker_builder, accepted_format):
    """
        根据给定的 worker_builder 构建包含对应 worker 的一个 Transform 类
    """

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
            image = convert_format(image=input_s["image"], output_format=accepted_format)
            if getattr(self, "worker", None) is None or len(self.random_item_s) > 0:
                # 需要新建/重建 worker
                setattr(self, "worker", worker_builder(**kwargs))

            res = self.worker(image)
            input_s["image"] = res

            return input_s

    # 使用 type() 动态创建 Transform_of_Given_Worker 的子类，这样才能保存到全局变量中
    cls = type(f'Transform_of_Given_Worker-{registered_name}', (Transform_of_Given_Worker,), {})

    return cls


if __name__ == '__main__':
    import os
    from PIL import Image
    import torchvision.transforms as transforms
    from kevin_dl.workers.transforms.for_images.utils import get_format
    from kevin_dl.utils.variable import root_dir
    from kevin_dl.workers.variable import TRANSFORMS

    image = Image.open(
        os.path.join(root_dir, "kevin_dl/workers/transforms/for_images/test/test_data/ILSVRC2012_val_00040001.JPEG"))

    name_ = ":for_images:torchvision:CenterCrop"

    ts = build_transform_for_torchvision(
        registered_name=name_, worker_builder=transforms.CenterCrop,
        accepted_format=Image_Format.TORCH_TENSOR
    )
    print(ts)

    TRANSFORMS.add(obj=ts, b_execute_now=False)

    output_s = TRANSFORMS.get(name=name_)(size=96)(
        input_s=dict(image=image)
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
