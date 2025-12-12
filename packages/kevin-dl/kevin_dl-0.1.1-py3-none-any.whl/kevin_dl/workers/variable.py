import os
import torch
from kevin_toolbox.computer_science.algorithm.registration import Registry

# 导入时的默认过滤规则
ignore_s = [
    {
        "func": lambda _, __, path: os.path.basename(path) in ["temp", "test", "__pycache__",
                                                               "_old_version"],
        "scope": ["root", "dirs"]
    },
]

"""
进程间共享变量
"""
MP_SHARED_VARS = Registry(uid="MP_SHARED_VARS")

"""
模型
"""
MODELS = Registry(uid="MODELS")
MODELS.collect_from_paths(
    path_ls=[os.path.join(os.path.dirname(__file__), "models"), ],
    ignore_s=ignore_s,
    b_execute_now=False
)

"""
数据扩增/变换

目前支持以下选项：

1. 图像类 for_images
    1. torchvision.transforms 中的变换器
        命名格式为 ":for_images:torchvision:xxx" 将调用 torchvision.transforms 下的变换器，比如：
            ":for_images:torchvision:CenterCrop" 对应于 torchvision.transforms.CenterCrop
    2. 自定义的变换器
        - blur
            - Gaussian_Blur     高斯模糊    ":for_images:blur:Gaussian_Blur"
            - Motion_Blur       运动模糊    ":for_images:blur:Motion_Blur"
        - color
            - Brightness_Shift  亮度调节    ":for_images:color:Brightness_Shift"
"""
TRANSFORMS = Registry(uid="TRANSFORMS")
TRANSFORMS.collect_from_paths(
    path_ls=[os.path.join(os.path.dirname(__file__), "transforms"), ],
    ignore_s=ignore_s,
    b_execute_now=False
)
from kevin_dl.workers.transforms.for_images.torchvision_ import collect_from_torchvision

collect_from_torchvision()

try:
    import albumentations
except:
    import warnings
    warnings.warn("albumentations is not installed, related features will not be available")
else:
    from kevin_dl.workers.transforms.for_images.albumentations_ import collect_from_albumentations

    collect_from_albumentations()
"""
数据集
"""
# 对于数据集的收集，需要忽略非package的文件夹（亦即没有 __init__.py 文件的）
ignore_s_for_dataset = [
                           {
                               "func": lambda b_is_dir, __, path: b_is_dir and "__init__.py" not in os.listdir(path),
                               "scope": ["root", "dirs"]
                           },
                       ] + ignore_s

DATASETS = Registry(uid="DATASETS")
DATASETS.collect_from_paths(
    path_ls=[os.path.join(os.path.dirname(__file__), "datasets"), ],
    ignore_s=ignore_s_for_dataset,
    b_execute_now=False
)
from kevin_dl.workers.datasets.cv.torchvision_ import collect_from_torchvision

collect_from_torchvision()

"""
优化器

目前支持以下选项：

1. torch 自带的优化器
    命名格式为 ":torch:optim:xxx" 将调用 torch.optim 下的优化器，比如：
        ":torch:optim:SGD" 对应于 torch.optim.SGD
2. 自定义的优化器
    将调用 optimizers 下自定义且注册到OPTIMIZERS中的优化器/返回优化器的函数。
        对于自定义优化器的要求：
            1. 输入参数中，必须包含 params 参数，该参数将用于传入一个 list of parameter groups dicts，具体可以参考这里：
                 https://pytorch.org/docs/stable/generated/torch.optim.SGD.html
            2. 包含 self.param_groups 属性以保存输入的 parameter groups dict；
            3. 支持通过使用函数 self.add_param_group() 来往 self.param_groups 中添加新的 parameter groups dict。
        补充要求（不强制要求）：
            1. 具有 state_dict() 方法来获取状态；
            2. 具有 load_state_dict() 方法来加载状态。
"""
OPTIMIZERS = Registry(uid="OPTIMIZERS")
for k, v in torch.optim.__dict__.items():
    if type(v) == type:
        OPTIMIZERS.add(obj=v, name=f':torch:optim:{k}', b_execute_now=False)
OPTIMIZERS.collect_from_paths(
    path_ls=[os.path.join(os.path.dirname(__file__), "optimizers"), ],
    ignore_s=ignore_s,
    b_execute_now=False)

"""
算法执行器
"""
ALGORITHMS = Registry(uid="ALGORITHMS")
ALGORITHMS.collect_from_paths(
    path_ls=[os.path.join(os.path.dirname(__file__), "algorithms", "sombrero"),
             os.path.join(os.path.dirname(__file__), "algorithms", "mixup"),
             os.path.join(os.path.dirname(__file__), "algorithms", "for_liveness"),
             os.path.join(os.path.dirname(__file__), "algorithms", "magnitude_direction_decomposition"),],
    ignore_s=ignore_s,
    b_execute_now=False
)

"""
记录器
"""
LOGGERS = Registry(uid="LOGGERS")


