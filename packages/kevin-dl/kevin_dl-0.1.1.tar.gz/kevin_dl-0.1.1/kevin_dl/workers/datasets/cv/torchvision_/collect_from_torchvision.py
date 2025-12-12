import torchvision.datasets as datasets
from kevin_dl.workers.datasets.cv.torchvision_ import Build_Torchvision_Dataset


def collect_from_torchvision():
    from kevin_dl.workers.variable import DATASETS

    for k in datasets.__all__:
        name = f':cv:torchvision:{k}'
        if DATASETS.get(name=name, default=None) is None:
            DATASETS.add(obj=Build_Torchvision_Dataset(dataset_name=k),
                         name=name, b_execute_now=False)


if __name__ == '__main__':
    collect_from_torchvision()
    from kevin_dl.workers.variable import DATASETS
    from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format

    a = DATASETS.get(name=":cv:torchvision:CIFAR10")(root='~/data', train=True, download=True,
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
