import os
import copy
from collections import Counter
import warnings
import cv2
from PIL import Image
import numpy as np
from torch.utils.data import Dataset
from kevin_toolbox.data_flow.file import json_
from kevin_toolbox.computer_science.algorithm import for_seq
from kevin_dl.workers.transforms import Pipeline
from kevin_dl.workers.transforms.for_images.utils import Image_Format, get_format, convert_format
from kevin_dl.workers.datasets.utils.variable import Task_Type
from kevin_dl.workers.datasets.cv.captcha import Captcha_Maker
from kevin_dl.workers.variable import DATASETS
from kevin_dl.utils.ceph import read_image, read_file


@DATASETS.register(name=":cv:Captcha_Dataset:0.0")
class Captcha_Dataset(Dataset):
    """
        生成验证码图片数据集
            默认以 RGB 方式读取图片，也可以通过指定 b_bgr_order 参数来修改

        注意在 seed 非 None，且 dataloader 使用多进程加载数据时，应避免通过 set_seed 对随机种子进行修改，具体参考《Dataloader多进程复制问题》
    """

    def __init__(self, **kwargs):
        """
            参数：
                captcha_maker:                  <dict of paras/Captcha_Maker> 验证码图片生成器。
                                                    具体参考 Captcha_Maker 的介绍
                label_maker:                    <callable/file/dict of paras> 验证码文本（标签）生成器。
                                                    当给定值为函数时，要求其形式为 func(idx) ==> label
                                                    当给定值为文件，要求其为保存有 label_ls 列表的 json 文件。
                                                    当其给定值为 dict 时，要求其具有以下键值对：
                                                        - "options":        <list of str> 可选的标签文本
                                                        - "weights":        <list of float/int> 权重值
                cache_dir:                      <path> 缓存数据目录。
                                                    当指定有具体值时，且该目录存且其中的内容符合要求时（同时具有 dataset.json 文件和 images 文件夹），将直接从缓存中加载。
                                captcha_maker+label_maker 和 cache_dir 两个组合应至少指定其一，对于不同情况，其动作为：
                                    - 仅指定 maker：            实时生成数据
                                    - 仅指定 cache_dir 且缓存存在：      从缓存中加载数据集
                                    - 仅指定 cache_dir 且缓存不存在：     报错
                                    - 同时指定两者，但 cache_dir 不存在：   实时生成数据，但可以通过 preload_to_cache 来在给定 cache_dir 目录下生成缓存。
                                    - 同时指定两者，且 cache_dir 存在：    从缓存中加载数据集
                label_mapper:                   <callable/file/dict/str> label 映射器
                                                    默认情况下将使用构造成验证码图片所用的文本作为 label，而通过指定该参数，可以将原来是验证码的 label 按照指定的规则进行映射。
                                                    该参数在构造需要 label 是 index 的分类数据集时非常有用。
                                                    当给定值为函数时，要求其形式为 func(label_text) ==> dst
                                                    当给定值为 dict 时，将通过 label_mapper[label_text] ==> dst 的方式进行映射。
                                                    当给定值为文件路径时，要求其为保存有 mapper dict 的 json 文件。
                                                    当给定值为 str 时，支持以下模式：
                                                        - "index_sorted_by_alphabet":       汇总所有 label，并按照字母表顺序进行排序（升序）
                                                        - "index_sorted_by_frequency":      汇总所有 label，并按照每个 label 出现的频率进行排序（降序）
                dataset_size:                   <int> 数据集的大小
                transforms:                     <dict> 定义数据处理流程
                                                    构建 Pipeline 的设置，具体参考 workers.transforms.Pipeline
                b_bgr_order:                    <boolean> 是否按照 BGR 顺序读取图片
                                                    默认为 False，亦即使用 RGB 方式。
                output_contents:                <list of str> 需要添加到输出中的内容。
                                                    目前支持：
                                                        # 图像
                                                        "raw"  原始图像
                                                        "fin" 经过 transforms 处理后的图像
                                                        # 标签
                                                        "label"
                task_type:                      <str> 任务类型，有 "train" "test" "val" 可选
                                                    当设置为 "train" 时，每次调用 __getitem__(idx) 生成的数据都是随机的，即使 idx 一样也可能不同。
                                                    当设置为其他时，blur 中的随机种子将在每次调用 __getitem__(idx) 时被设置为
                                                        idx+seed，以保证相同 idx 下生成的数据是相同的。
                                                    默认设置为 "train"。
                seed:                           <int>  在生成测试数据时，亦即 task_type="test" 时将模糊等操作等的随机种子固定为
                                                    seed + index 以保证每次生成的测试数据都是一致的。
                b_auto_save_image_to_cache:     <boolean> 在读取数据时，若需要实时生成图片，是否将生成的图片自动保存到 cache 中。
                                                    默认为 True。该参数只有在指定有 cache_dir 时，才会起效。

            数据处理流程：
                raw ==> (transforms) ==> fin

            返回：
                res:            <dict> 内容依据 output_contents 而定
        """
        super().__init__()

        # 默认参数
        paras = {
            # 数据集
            "captcha_maker": None,
            "label_maker": None,
            "cache_dir": None,
            "label_mapper": None,
            "dataset_size": None,
            # 数据处理
            "transforms": None,
            "b_bgr_order": False,
            "task_type": "train",
            "seed": 114514,
            # 输出
            "output_contents": ("fin", "label"),
            #
            "b_auto_save_image_to_cache": True
        }

        # 获取参数
        paras.update(kwargs)

        # 校验参数
        assert isinstance(paras["dataset_size"], (int,)) and paras["dataset_size"] > 0
        assert not all([paras[k] is None for k in ["captcha_maker", "label_maker", "cache_dir"]])
        for k in ["cache_dir", "label_maker", "label_mapper"]:
            if isinstance(paras[k], str):
                paras[k] = os.path.expanduser(paras[k])
        assert isinstance(paras["transforms"], (dict,))
        if paras["captcha_maker"] is not None:
            if isinstance(paras["captcha_maker"], (dict,)):
                paras["captcha_maker"].setdefault("seed", paras["seed"])
            paras["captcha_maker"] = Captcha_Maker(**paras["captcha_maker"])
            assert isinstance(paras["captcha_maker"], (Captcha_Maker,))

        # 构造 data_s
        self.data_s, self._b_load_from_cache = self.load_data_s(paras=paras)

        # 构建 pipeline
        self.pipeline = Pipeline(**paras["transforms"])
        self.pipeline.set_rng(seed=paras["seed"], b_delayed_set_rng=True, b_seed_wrt_worker_id=True)

        self.paras = paras

    def set_rng(self, seed=None):
        """
            设定/重新设定随机采样器

            参数：
                seed:                   <int> 随机种子
        """
        warnings.deprecated('由于该函数在多进程下具有不可控行为，因此废弃。')
        self.paras["seed"] = seed
        self.pipeline.set_rng(seed=self.paras["seed"])

    @staticmethod
    def load_data_s(paras):
        """
            根据配置构造 data_s
        """
        b_load_from_cache = False
        if paras["cache_dir"] is not None and os.path.isdir(paras["cache_dir"]) and {"dataset.json", "images"}.issubset(
                set(os.listdir(paras["cache_dir"]))):
            # 缓存目录 cache_dir 存在且格式正确，从中读取数据构造 data_s
            data_s = json_.read(file_path=os.path.join(paras["cache_dir"], "dataset.json"),
                                b_use_suggested_converter=True)
            assert "image_path" in data_s and "label" in data_s
            assert len(data_s["image_path"]) == len(data_s["label"])
            #
            label_mapper = os.path.join(paras["cache_dir"], "label_mapper.json") if paras["label_mapper"
                                                                                    ] is None else paras["label_mapper"]
            if os.path.isfile(label_mapper):
                label_mapper = json_.read(file_path=label_mapper, b_use_suggested_converter=True)
                assert isinstance(label_mapper, dict)
                if "label_raw" not in data_s:
                    data_s["label_raw"] = data_s["label"].copy()
                data_s["label"] = [label_mapper[i] for i in data_s["label_raw"]]
            b_load_from_cache = True
        else:
            data_s = dict()
            # 根据 label_maker 生成 data_s 中的 label
            label_maker = paras["label_maker"]
            if isinstance(label_maker, (str,)):
                # 从文件读取
                assert os.path.isfile(label_maker), \
                    f"label_maker file not exists: {paras['label_maker']}"
                data_s["label"] = json_.read(file_path=paras['label_maker'], b_use_suggested_converter=True)
            elif callable(label_maker):
                data_s["label"] = [label_maker(i) for i in range(paras["dataset_size"])]
            else:
                assert isinstance(label_maker, (dict,))
                if "options" in label_maker and "weights" in label_maker:
                    if not isinstance(label_maker["weights"], (list, tuple,)):
                        label_maker["weights"] = [label_maker["weights"]] * len(label_maker["options"])
                    assert len(label_maker["options"]) == len(label_maker["weights"])
                    label_maker["weights"] = np.array(label_maker["weights"]) / np.sum(label_maker["weights"])
                    data_s["label"] = []
                    for opt, w in zip(label_maker["options"], label_maker["weights"]):
                        data_s["label"] += [opt] * int(np.ceil(paras["dataset_size"] * w))
                else:
                    raise ValueError(f"label_maker is not valid, because has keys {label_maker.keys()}")
            data_s["label"] = [f'{i}' for i in data_s["label"]]

            # 根据 label_mapper 对 label 进行映射
            label_mapper = paras["label_mapper"]
            if label_mapper is not None:
                data_s["label_raw"] = data_s["label"].copy()
                if isinstance(label_mapper, (str,)):
                    if os.path.isfile(label_mapper):
                        label_mapper = json_.read(file_path=label_mapper, b_use_suggested_converter=True)
                    elif label_mapper == "index_sorted_by_alphabet":
                        temp = list(set(data_s["label"]))
                        temp.sort()
                        label_mapper = {k: i for i, k in enumerate(temp)}
                    elif label_mapper == "index_sorted_by_frequency":
                        temp = dict(Counter(data_s["label"]))
                        temp = [(freq, label) for label, freq in temp.items()]
                        temp.sort(key=lambda x: x[0], reverse=True)
                        label_mapper = {k[1]: i for i, k in enumerate(temp)}
                if isinstance(label_mapper, (dict,)):
                    data_s["label"] = [label_mapper[i] for i in data_s["label"]]
                elif callable(label_mapper):
                    data_s["label"] = [label_mapper(i) for i in data_s["label"]]
                else:
                    raise ValueError("label_mapper is not callable or dict")

            # 将 image_path 置为 None 从而引导实时生成数据。
            data_s["image_path"] = [None] * len(data_s["label"])

        #   采样为 dataset_size 大小
        idx_ls = for_seq.sample_subset_most_evenly(inputs=list(range(len(data_s["label"]))),
                                                   nums=paras["dataset_size"], seed=paras["seed"])
        for k, v in data_s.items():
            data_s[k] = [v[i] for i in idx_ls]
        return data_s, b_load_from_cache

    def _get_data(self, idx, b_save_to_cache=False):
        image_path, label = self.data_s["image_path"][idx], self.data_s["label"][idx]
        if image_path is not None:
            image = read_image(file_path=os.path.join(self.paras["cache_dir"], "images", image_path),
                               b_bgr_order=self.paras["b_bgr_order"])
        else:
            text = self.data_s["label_raw"][idx] if "label_raw" in self.data_s else label
            image = np.array(self.paras["captcha_maker"].generate(text=text))
            bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if self.paras["b_bgr_order"]:
                image = bgr_image
            if b_save_to_cache and self.paras["cache_dir"] is not None:
                image_path = os.path.join(self.paras["cache_dir"], "images", f'{idx}.png')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                cv2.imwrite(filename=image_path, img=bgr_image)
                self.data_s["image_path"][idx] = f'{idx}.png'

        return image, label

    def preload_to_cache(self, cache_dir=None):
        """
            将数据预加载到 cache 中
        """
        cache_dir = self.paras["cache_dir"] if cache_dir is None else cache_dir
        assert cache_dir is not None, \
            f"cache_dir is None"
        if self._b_load_from_cache and cache_dir == self.paras["cache_dir"]:
            return

        for idx in range(len(self)):
            self._get_data(idx=idx, b_save_to_cache=True)
        json_.write(content=self.data_s, file_path=os.path.join(cache_dir, "dataset.json"),
                    b_use_suggested_converter=True)

    def __len__(self):
        return len(self.data_s["image_path"])

    def __getitem__(self, idx):
        if Task_Type(self.paras["task_type"]) is not Task_Type.Train:
            self.pipeline.set_rng(seed=self.paras["seed"] + idx if self.paras["seed"] is not None else idx,
                                  b_delayed_set_rng=False, b_seed_wrt_worker_id=False)

        temp_s = dict()
        temp_s["raw"], temp_s["label"] = self._get_data(idx=idx,
                                                        b_save_to_cache=self.paras["b_auto_save_image_to_cache"])
        temp_s["fin"] = self.pipeline(input_s=dict(image=copy.deepcopy(temp_s["raw"])))["image"]

        res = {k: v[idx] for k, v in self.data_s.items()}
        res.update(temp_s)
        res = {k: res.get(k, None) for k in self.paras["output_contents"]}
        for k in res.keys():
            if get_format(res[k]) is Image_Format.PIL_IMAGE:
                res[k] = convert_format(res[k], input_format=Image_Format.PIL_IMAGE,
                                        output_format=Image_Format.NP_ARRAY)

        return res


if __name__ == '__main__':
    def get_visible_ascii_chars():
        """
        返回所有标准 ASCII 中的可见（非空）字符列表。
        范围是 ASCII 编码 32 到 126，包括空格、标点、数字、字母等。

        返回：
            List[str]: 95 个可见字符组成的列表
        """
        return [chr(i) for i in range(32, 127)]


    size = 64

    a = Captcha_Dataset(
        captcha_maker={
            #
            "width": size,
            "height": size,
            "font_size": int(size * 0.8),
            "color_options_of_text": None,
            "color_of_bg": 255,
            #
            "max_offset_of_text": (0.5, 0.5),
            "b_use_transforms": True,
            "transforms": [
                {
                    "name": ":for_images:torchvision:ToTensor",
                    "paras": {}
                },
                {
                    "name": ":for_images:torchvision:RandomAffine",
                    "paras": {
                        "degrees": 30, "translate": (0.05, 0.1), "shear": 30, "fill": (1.0, 1.0, 1.0),
                    }
                },
                {
                    "name": ":for_images:torchvision:GaussianBlur",
                    "paras": {
                        "kernel_size": 3, "sigma": (0.1, 1.5)
                    }
                },

                {
                    "name": ":for_images:torchvision:ColorJitter",
                    "paras": {
                        "brightness": 0.3, "contrast": 0.3, "saturation": 0.3
                    }
                }
            ],
            "b_add_noise_line": True,
            "color_options_of_line": ("gray",),
            "b_add_noise_point": True,
        },
        label_maker={
            "options": get_visible_ascii_chars(),
            "weights": 1.0,
        },
        cache_dir=os.path.join(os.path.dirname(__file__), "temp", "example"),
        dataset_size=1000,
        transforms={
            "settings": [
                # 添加噪声
                {
                    "name": ':for_images:torchvision:RandomGrayscale',
                    "paras": {
                        "p": 0.2
                    }
                },
                {
                    "name": ':for_images:blur:Gaussian_Blur',
                    "paras": {
                        "sigma": {
                            "p_type": "float",
                            "p_prob": "uniform",
                            "high": 1,
                            "low": 0,
                        }
                    }
                },
                #
                {
                    "name": ':for_images:torchvision:Resize',
                    "paras": {
                        "size": (224, 224)
                    }
                }
            ]
        },
        task_type="train",
        output_contents=["raw", "fin", "label"],
        seed=12345,
    )
    print(a[0])

    a.preload_to_cache()

    Image.fromarray((a[0]['raw'])).show()
    print(a[0]['fin'].shape)
    print(a[0]['label'])

    Image.fromarray((a[0]['raw'])).show()

    json_.write(content={k: i for i, k in enumerate(get_visible_ascii_chars())},
                file_path=os.path.join(os.path.dirname(__file__), "temp", "example", "label_mapper.json"),
                b_use_suggested_converter=True)
