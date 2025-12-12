import os
import warnings
from collections import defaultdict
from torch.utils.data import Dataset
from kevin_toolbox.data_flow.file import json_
from kevin_toolbox.computer_science.algorithm.for_seq import sample_subset_most_evenly
from kevin_toolbox.math.utils import split_integer_most_evenly
from kevin_toolbox.patches.for_numpy.random import get_rng
from kevin_dl.workers.datasets.adjuster.utils import parse_func
from kevin_dl.workers.variable import DATASETS


@DATASETS.register(name=":adjuster:proportion_adjuster")
def proportion_adjuster(**kwargs):
    """
        基于 Proportion_Adjuster 构建，返回 idx_map_ls
            可以进一步通过 torch.utils.data.Subset(dataset, idx_map_ls) 构建改变比例后的数据集

        参数：
            与 Proportion_Adjuster 相同
    """
    adjuster = Proportion_Adjuster(**kwargs)
    return adjuster.idx_map_ls


@DATASETS.register(name=":adjuster:Proportion_Adjuster")
class Proportion_Adjuster(Dataset):
    """
        对给定数据集中的数据按照要求调整比例并构建为一个新的数据集
    """

    def __init__(self, **kwargs):
        """
            参数：
                cond_s_ls:                      <list of dict> 通过过滤函数的形式划分分组，并指定要各个分组数据占整体的比例。
                                                    列表的形式为：
                                                        [
                                                            {
                                                                "filter":   <callable>,
                                                                "ratio":    <float>
                                                            },
                                                            ...
                                                        ]
                                                    其中每个元素中的键值对的要求如下：
                                                        - "filter":     形如 func(data) ==> boolean 的函数，当该函数满足时，
                                                                        表示该元素对应的分组。
                                                        - "ratio":      该分组的数据应占整体数据的比例。
                                                                        当 b_normalize_ratio=True 且各个分组的 ratio 和不为1时，将自动进行归一化
                label_cond_s:                   <dict> 通过某个字段取值的形式划分分组，并指定要各个分组数据占整体的比例。
                                                    字典的形式为:
                                                        {
                                                            "label_func":   <callable>,
                                                            "ratio_s":      {<label_value> or <label_filter>: <float>, ...} or float
                                                        }
                                                    其中键值对的要求如下：
                                                        - "label_func":     形如 func(data) ==> hashable 的函数，
                                                                            将以其输出值作为该 data 的 label_value。
                                                        - "ratio_s":        指定各个 label_value 对应的分组或者 label_filter 通过的分组的比例。
                                                                            当设置为 float 时，表示以 data 的 label_value 作为分组，通过每个分组的 ratio 都一样。
                                    以上两个参数仅指定一个即可，同时指定时，先以 cond_s_ls 划分分组，再使用 label_cond_s 对剩余的划分分组。
                src_dataset:                    <Dataset> 原始数据集。
                b_quick_loading:                <boolean> 是否尝试使用快速加载。
                                                    为何需要快速加载？
                                                        为了对 src_dataset 中的数据集进行分组，要求对其进行一次完整的读取。由于数据读取时一般涉及到
                                                        图片的读取和处理，而这往往是非常耗时的，而很多时候我们在进行分组时并不需要用到图片信息。
                                                        我们称不进行额外图片读取的数据集加载方式，为快速加载。
                                                    目前支持快速读取的数据集有：
                                                        - :cv:Image_Dataset_v2:0.1
                b_normalize_ratio:              <boolean> 是否对各个分组的 ratio 进行归一化。
                                                    默认为True，此时分组的 ratio 将进行归一化，归一化后的值表示该分组在新数据集中的占比。
                                                    当设置为 False，此时分组的 ratio 表示要将分组中的数据量扩增or缩减至原来的多少比例。
                dst_num:                        <int/float> 待构建的目标数据集的大小。
                                                    当设置为 float 时，表示在 src_dataset 的大小基础上乘以多少。
                                                    默认为 1.0。
                                                    该参数仅在 b_normalize_ratio=True 时起效。
                record_dir:                     <path> 用于保存 src_dataset 到 dst_dataset 的 idx 映射信息的目录。
                                                    默认为 None。
                b_use_record_if_exists:         <boolean> 是否尝试从已有的 record_dir 中直接加载映射。
                                                    默认为 True。
                                                    当可以直接加载映射时，将不会再根据 cond_s_ls 和 label_cond_s 去构建映射，而直接使用已加载的映射。
                b_save_record:                  <boolean> 是否尝试保存 record 以便后续快速加载。
                seed, rng:                      设定随机发生器
        """
        super().__init__()

        # 默认参数
        paras = {
            # 分组条件
            "cond_s_ls": None,
            "label_cond_s": None,
            "b_normalize_ratio": True,
            # 目标数据集
            "dst_num": 1.0,
            # 原始数据集
            "src_dataset": None,
            "b_quick_loading": True,
            #
            "record_dir": None,
            "b_use_record_if_exists": True,
            "b_save_record": False,
            #
            "seed": None,
            "rng": None,
        }

        # 获取参数
        paras.update(kwargs)

        # 校验参数
        if paras["record_dir"] is not None:
            paras["record_dir"] = os.path.expanduser(paras["record_dir"])
        assert isinstance(paras["src_dataset"], (Dataset,))
        assert isinstance(paras["cond_s_ls"], (list, tuple,)) or paras["cond_s_ls"] is None
        assert isinstance(paras["label_cond_s"], (dict,)) or paras["label_cond_s"] is None
        if paras["cond_s_ls"] is not None:
            for it in paras["cond_s_ls"]:
                it["filter"] = parse_func(it["filter"])
        if paras["label_cond_s"] is not None:
            paras["label_cond_s"]["label_func"] = parse_func(paras["label_cond_s"]["label_func"])
            if isinstance(paras["label_cond_s"]["ratio_s"], dict):
                temp = dict()
                for k, v in paras["label_cond_s"]["ratio_s"].items():
                    if isinstance(k, str) and k.startswith("<eval>"):
                        temp[parse_func(k)] = v
                    else:
                        temp[k] = v
                paras["label_cond_s"]["ratio_s"] = temp

        self.src_dataset = paras["src_dataset"]
        paras["dst_num"] = int(paras["dst_num"] * len(self.src_dataset)) if isinstance(paras["dst_num"],
                                                                                       float) else paras["dst_num"]
        self.rng = get_rng(seed=paras["seed"], rng=paras["rng"])

        # 建立 src_idx 到 dst_idx 的映射
        self.idx_map_ls, self.group_s = None, None
        self.b_use_record = False
        if paras["b_use_record_if_exists"]:
            self.idx_map_ls, self.group_s = self._load_record(record_dir=paras["record_dir"])
        if self.idx_map_ls is None:
            self.src_dataset_fetcher = self._build_dataset_fetcher(dataset=self.src_dataset,
                                                                   b_quick_loading=paras["b_quick_loading"])
            #
            self.group_s = self._build_group_s(
                cond_s_ls=paras["cond_s_ls"], label_cond_s=paras["label_cond_s"],
                src_dataset_len=len(self.src_dataset), src_dataset_fetcher=self.src_dataset_fetcher
            )
            self.idx_map_ls = self._build_idx_map(
                group_s=self.group_s, dst_num=paras["dst_num"],
                b_normalize_ratio=paras["b_normalize_ratio"], rng=self.rng
            )
            if paras["b_save_record"]:
                self._save_record(record_dir=paras["record_dir"], idx_map_ls=self.idx_map_ls, group_s=self.group_s)
        else:
            self.b_use_record = True

        self.paras = paras

    @staticmethod
    def _build_dataset_fetcher(dataset, b_quick_loading):
        fetcher = lambda idx: dataset[idx]
        if b_quick_loading:
            from kevin_dl.workers.variable import DATASETS

            if isinstance(dataset, tuple(
                    DATASETS.get(name=n) for n in
                    (":cv:Image_Dataset_v2:0.1", ":cv:classification:Imagenet_Dataset"))):
                fetcher = lambda idx: {k: v[idx] for k, v in dataset.data_s.items()}
        else:
            warnings.warn(f"quick loading is not supported for this dataset {dataset.__class__}")
        return fetcher

    @staticmethod
    def _load_record(record_dir):
        """加载已有的映射"""
        idx_map_ls, group_s = None, None
        if record_dir is None:
            return idx_map_ls, group_s

        if os.path.isdir(record_dir):
            assert os.path.isfile(os.path.join(record_dir, "idx_map_ls.json"))
            idx_map_ls = json_.read(file_path=os.path.join(record_dir, "idx_map_ls.json"),
                                    b_use_suggested_converter=True)
            if os.path.isfile(os.path.join(record_dir, "group_s.json")):
                group_s = json_.read(file_path=os.path.join(record_dir, "group_s.json"),
                                     b_use_suggested_converter=True)
        if idx_map_ls is None:
            warnings.warn(f'failed to load record from {record_dir}')
        elif group_s is None:
            warnings.warn(f'incomplete record, group_s will be None')
        return idx_map_ls, group_s

    @staticmethod
    def _save_record(record_dir, idx_map_ls, group_s):
        """保存映射"""
        if record_dir is None:
            return False
        os.makedirs(record_dir, exist_ok=True)
        if idx_map_ls is None:
            warnings.warn(f'failed to save record, because idx_map_ls is None')
            return False
        json_.write(file_path=os.path.join(record_dir, "idx_map_ls.json"),
                    content=idx_map_ls, b_use_suggested_converter=True)
        if group_s is None:
            warnings.warn(f'will create an incomplete record, because group_s is None')
        else:
            func_count = 0
            for k in list(group_s.keys()):
                if callable(k[1]):
                    group_s[(k[0], f'func_{func_count}')] = group_s.pop(k)
                    func_count += 1
            json_.write(file_path=os.path.join(record_dir, "group_s.json"),
                        content=group_s, b_use_suggested_converter=True)
        return True

    @staticmethod
    def _build_group_s(cond_s_ls, label_cond_s, src_dataset_len, src_dataset_fetcher):
        """根据 cond_s_ls 和 label_cond_s 对原始数据集中的数据进行分组"""
        group_s = defaultdict(lambda: {"src_idx": [], "dst_idx": [], "ratio": 0, "nums": 0})

        for idx in range(src_dataset_len):
            data = src_dataset_fetcher(idx=idx)

            #   from cond_s_ls
            b_pick = False
            if cond_s_ls is not None:
                for i, cond_s in enumerate(cond_s_ls):
                    group_name = ("cond_s_ls", i)
                    group_s[group_name]["ratio"] = cond_s["ratio"]
                    if cond_s["filter"](data):
                        group_s[group_name]["src_idx"].append(idx)
                        b_pick = True
                        break

            #   from label_cond_s
            if not b_pick and label_cond_s is not None:
                if not isinstance(label_cond_s["ratio_s"], dict):
                    label = label_cond_s["label_func"](data)
                    group_name = ("label_cond_s", label)
                    group_s[group_name]["ratio"] = label_cond_s["ratio_s"]
                    group_s[group_name]["src_idx"].append(idx)
                else:
                    for label_check, ratio in label_cond_s["ratio_s"].items():
                        group_name = ("label_cond_s", label_check)
                        group_s[group_name]["ratio"] = ratio
                        label = label_cond_s["label_func"](data)
                        if (callable(label_check) and label_check(label)) or label_check == label:
                            group_s[group_name]["src_idx"].append(idx)
                            break
        return group_s

    @staticmethod
    def _build_idx_map(group_s, dst_num, b_normalize_ratio, rng):
        """根据各个分组指定的比例，构建到目标数据集的映射"""
        idx_map_ls = []

        # 根据 ratio 计算 nums
        if b_normalize_ratio:
            temp = sum([group_s[k]["ratio"] for k in group_s.keys()])
            temp_2 = 0
            for k in group_s.keys():
                group_s[k]["ratio"] /= temp
                group_s[k]["nums"] = int(group_s[k]["ratio"] * dst_num)
                temp_2 += group_s[k]["nums"]
            if dst_num != temp_2:
                if dst_num > temp_2:
                    group_names = list(group_s.keys())
                else:
                    group_names = [k for k in group_s.keys() if group_s[k]["nums"] != 0]
                group_names = sorted(group_names)
                res = split_integer_most_evenly(x=abs(dst_num - temp_2), group_nums=len(group_names))
                for i, group_name in zip(res, group_names):
                    group_s[group_name]["nums"] += i if dst_num > temp_2 else -i
        else:
            for k in group_s.keys():
                group_s[k]["nums"] = int(group_s[k]["ratio"] * len(group_s[k]["src_idx"]))

        # 构建映射
        for i, it in enumerate(group_s.values()):
            it["dst_idx"] = sample_subset_most_evenly(
                inputs=it["src_idx"], nums=it["nums"], rng=rng, b_shuffle_the_tail=True)
            idx_map_ls += it["dst_idx"]

        return idx_map_ls

    def __len__(self):
        return len(self.idx_map_ls)

    def __getitem__(self, idx):
        return self.src_dataset[self.idx_map_ls[idx]]


if __name__ == "__main__":
    from kevin_dl.workers.datasets.cv.torchvision_ import Build_Torchvision_Dataset
    from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format

    a = Build_Torchvision_Dataset(dataset_name="CIFAR10")(root='~/data', train=True, download=True,
                                                          transform={
                                                              "settings": []
                                                          },
                                                          seed=114514)
    b = Proportion_Adjuster(
        src_dataset=a, label_cond_s={
            "label_func": "<eval>lambda x: x[1]",
            "ratio_s": {1: 0.4, 2: 0.7}
        },
        dst_num=1000,
        record_dir=os.path.join(os.path.dirname(__file__), "test", "temp"),
        b_quick_loading=True,
        b_use_record_if_exists=True,
        seed=1919810
    )
    print(b[0])
    print(len(b))

    convert_format(image=b[0][0], output_format=Image_Format.PIL_IMAGE).show()
