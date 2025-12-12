import torch
import torchvision.datasets as datasets
import kevin_toolbox.nested_dict_list as ndl
from kevin_dl.workers.transforms import Pipeline
from kevin_dl.workers.datasets.utils.variable import Task_Type


class Build_Torchvision_Dataset:
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name

    def __call__(self, seed=None, task_type=None, **kwargs):
        """
            构建 torchvision 内置的数据集

            参数：
                dataset_name:           <str> 要构建的数据集类名
                kwargs:                 <dict of paras> 构建数据集实例时，传入类初始化函数中的参数
                                        本函数将会自动检测 kwargs 中的以下参数并进行解释or替换：
                                            - transform/target_transform:       若为 dict 则使用 Pipeline() 进行构建
                seed:     <int> 覆盖使用 Pipeline() 进行构建时设定的随机种子。
        """
        Cls = getattr(datasets, self.dataset_name, None)
        assert type(Cls) == type, f'there is no {self.dataset_name} in torchvision'
        #
        kwargs = ndl.copy_(var=kwargs, b_deepcopy=True)
        for k in ["transform", "target_transform"]:
            if k in kwargs and isinstance(kwargs[k], (dict,)) and "settings" in kwargs[k]:
                if seed is not None:
                    kwargs[k]["seed"] = seed
                kwargs[k].setdefault("mapping_ls_for_inputs", ["image"])
                kwargs[k].setdefault("mapping_ls_for_outputs", "image")
                kwargs[k]["b_include_details"] = False
                kwargs[k] = Pipeline(**kwargs[k])
        #
        if "train" not in kwargs and task_type is not None:
            kwargs["train"] = Task_Type(task_type) is Task_Type.Train

        try:
            return Cls(**kwargs)
        except:
            raise Exception(f"failed to build {self.dataset_name} in torchvision with paras {kwargs}")


if __name__ == '__main__':
    from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format

    a = Build_Torchvision_Dataset(dataset_name="CIFAR10")(root='~/data', train=True, download=True,
                                                          transform={
                                                              "settings": [
                                                                  # 归一化
                                                                  {
                                                                      "name": ':for_images:torchvision:ToTensor',
                                                                      "paras": {}
                                                                  },
                                                                  {
                                                                      "name": ':for_images:torchvision:Normalize',
                                                                      "paras": {
                                                                          "mean": (0.4914, 0.4822, 0.4465),
                                                                          "std": (0.2023, 0.1994, 0.2010)
                                                                      }
                                                                  }
                                                              ]
                                                          },
                                                          seed=114514)
    print(a[0])

    convert_format(image=a[0][0], output_format=Image_Format.PIL_IMAGE).show()
