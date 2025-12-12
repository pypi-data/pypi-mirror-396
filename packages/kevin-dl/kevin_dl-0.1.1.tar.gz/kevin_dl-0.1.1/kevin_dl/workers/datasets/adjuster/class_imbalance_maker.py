import os
import numpy as np
from kevin_dl.workers.datasets.adjuster import Proportion_Adjuster
from kevin_dl.workers.datasets.adjuster.utils import imbalanced_dist, parse_func
from kevin_dl.workers.variable import DATASETS

imbalanced_dist_s = {
    "power_law": imbalanced_dist.power_law,
    "exponential_decay": imbalanced_dist.exponential_decay,
    "step_decay": imbalanced_dist.step_decay,
}

class_order_func_s = {
    "ascending": lambda label_ls, *args: np.argsort(label_ls),
    "descending": lambda label_ls, *args: np.argsort(-np.asarray(label_ls)),
    "randomly": lambda label_ls, rng: rng.permutation(range(len(label_ls))),
}


@DATASETS.register(name=":adjuster:class_imbalance_maker")
def class_imbalance_maker(**kwargs):
    """
        基于 Proportion_Adjuster 构建，返回 idx_map_ls
            可以进一步通过 torch.utils.data.Subset(dataset, idx_map_ls) 构建改变比例后的数据集

        参数：
            与 Proportion_Adjuster 相同
    """
    adjuster = Class_Imbalance_Maker(**kwargs)
    return adjuster.idx_map_ls


@DATASETS.register(name=":adjuster:Class_Imbalance_Maker")
class Class_Imbalance_Maker(Proportion_Adjuster):
    """
        用于构建类别不均衡的分类数据集
    """

    def __init__(self, **kwargs):
        """
            参数：
                imbalanced_dist:                <dict> 用于指定生成各个类别分组占比的分布。
                                                    形式为：
                                                        {
                                                            "type_":    <str>,
                                                            "paras":    <dict of paras>
                                                        },
                                                    其中 type_ 指定分布的类型，目前有以下可选值：
                                                        - "exponential_decay":      类别样本数按照指数下降。
                                                                    在 paras 中需要指定：
                                                                        - gamma:        <float> 失衡因子。 0~1 之间，越大越平衡。
                                                        - "power_law":              按照幂律分布生成类别样本数的比例。
                                                                    在 paras 中需要指定：
                                                                        - alpha:        <float> 幂律分布的指数参数，控制分布的陡峭程度。
                                                                        值越大，分布越陡峭，即长尾效应越明显。
                                                        - "step_decay":             按照阶梯式衰减生成类别样本比例分布。
                                                                    在 paras 中需要指定：
                                                                        - step_width:   <int/float> 每个阶梯包含的类别数。
                                                                                当设置为小于 1.0 时，将解释为 step_width=math.ceil(step_width*cls_nums)
                                                                        - decay_ratio:  <float> 每个阶梯之间的比例衰减因子，取值越小，不平衡程度越高。
                label_func:                     <callable/str> 指定获取类别标签的方式。
                                                    形如 func(data) ==> hashable 的函数。
                class_order_func:               <callable/str> 类别的排序方式。
                                                    形如 func(label_ls, rng) ==> order_ls 的函数。
                                                    比如 order_ls=[2,0,1] 表示应该将 label_ls 中的第2个类别放到第0个位置，第0个类别放到第1个位置。
                                                    也支持通过以下值来指定使用内部已实现的函数：
                                                        - "ascending"       升序
                                                        - "descending"      降序
                                                        - "randomly"        随机（默认）
                                以上函数相关参数均支持使用 str 指定，此时要求当其以<eval>开头时，将使用 eval() 进行解释。
                dst_num:                        <int/float> 待构建的目标数据集的大小。
                                                    当设置为 float 时，表示在 src_dataset 的大小基础上乘以多少。
                                                    默认为 1.0。
                max_cls_size:                   <int/float> 每个类别的最大样本数量。
                                                    当设置为 float 时，表示在 样本最多的类别的样本数量 的基础上乘以多少。
                                以上两个参数仅需指定一个，同时指定时，以后者为准。
            其余参数请参考 Proportion_Adjuster 中的介绍：
                src_dataset:                    <Dataset> 原始数据集。
                b_quick_loading:                <boolean> 是否尝试使用快速加载。

                record_dir:                     <path> 用于保存 src_dataset 到 dst_dataset 的 idx 映射信息的目录。
                b_use_record_if_exists:         <boolean> 是否尝试从已有的 record_dir 中直接加载映射。
                b_save_record:                  <boolean> 是否尝试保存 record 以便后续快速加载。
                seed, rng:                      设定随机发生器
        """
        # 默认参数
        paras = {
            # 分组条件
            "imbalanced_dist": None,
            "label_func": None,
            "class_order_func": "randomly",
            # 目标数据集
            "max_cls_size": None,
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
        assert paras["label_func"] is not None
        assert paras["imbalanced_dist"] is not None and paras["imbalanced_dist"]["type_"] in imbalanced_dist_s
        dist_func = lambda cls_nums: imbalanced_dist_s[paras["imbalanced_dist"]["type_"]](
            cls_nums=cls_nums, **paras["imbalanced_dist"]["paras"]
        )
        if isinstance(paras["class_order_func"], str) and paras["class_order_func"] in class_order_func_s:
            class_order_func = class_order_func_s[paras["class_order_func"]]
        else:
            class_order_func = parse_func(paras["class_order_func"])
        label_cond_s = {"label_func": paras["label_func"], "ratio_s": 1.0}
        #
        super().__init__(
            label_cond_s=label_cond_s, b_normalize_ratio=False,
            src_dataset=paras["src_dataset"], b_quick_loading=paras["b_quick_loading"],
            record_dir=paras["record_dir"], b_use_record_if_exists=paras["b_use_record_if_exists"],
            seed=paras["seed"], rng=paras["rng"], b_save_record=False
        )
        if not self.b_use_record:
            # 根据指定的 imbalanced_dist 调整各个分组中的 ratio
            imb_dist = dist_func(len(self.group_s))
            group_keys = list(self.group_s.keys())
            class_order_ls = class_order_func([j for i, j in group_keys], self.rng)
            group_keys = [group_keys[i] for i in class_order_ls]
            for i, group_key in enumerate(group_keys):
                self.group_s[group_key]["ratio"] = imb_dist[i]
                self.group_s[group_key]["dst_idx"].clear()
            #
            if paras["max_cls_size"] is not None:
                max_cls_size = paras["max_cls_size"]
                if isinstance(max_cls_size, float):
                    max_cls_size = int(max([len(v_s["src_idx"]) for v_s in self.group_s.values()]) * max_cls_size)
                temp = imb_dist / max(imb_dist)
                dst_num = int(np.ceil(sum(temp * max_cls_size)))
            else:
                dst_num = self.paras["dst_num"]
            self.idx_map_ls = self._build_idx_map(
                group_s=self.group_s, dst_num=dst_num,
                b_normalize_ratio=True, rng=self.rng,
            )
            if paras["b_save_record"]:
                self._save_record(record_dir=paras["record_dir"], idx_map_ls=self.idx_map_ls, group_s=self.group_s)

        self.paras = paras


if __name__ == "__main__":
    from collections import defaultdict
    from kevin_toolbox.patches.for_matplotlib import common_charts
    from kevin_dl.workers.datasets.cv.torchvision_ import Build_Torchvision_Dataset
    from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format

    a = Build_Torchvision_Dataset(dataset_name="CIFAR10")(
        root='~/data', train=True, download=True,
        transform={
            "settings": []
        },
        seed=114514)
    b = Class_Imbalance_Maker(
        imbalanced_dist={
            "type_": "exponential_decay",
            "paras": {"gamma": 1 / 20}
        }, class_order_func="ascending",
        max_cls_size=1.0,
        src_dataset=a, label_func="<eval>lambda x: x[1]",
        record_dir=os.path.join(os.path.dirname(__file__), "test", "temp", "class_imbalance_maker"),
        b_quick_loading=True, b_use_record_if_exists=True,
        seed=1919810
    )
    # 统计各个分类的样本数量
    count_s = defaultdict(int)
    labels = []
    for i in b:
        count_s[i[1]] += 1
        labels.append(i[1])
    print(count_s)
    common_charts.plot_distribution(data_s={"label": labels}, title="imb cifa 10", type_="category", x_name="label")

    print(b[0])
    print(len(b))

    convert_format(image=b[0][0], output_format=Image_Format.PIL_IMAGE).show()
