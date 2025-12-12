import math
import warnings
import multiprocessing as mp
import numpy as np
import torch
from torch.utils.data import Dataset
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.computer_science.algorithm.for_seq import chunk_generator
from kevin_toolbox.patches.for_numpy.random import get_rng
from kevin_dl.workers.datasets.utils.variable import Task_Type
from kevin_dl.workers.datasets.adjuster.utils import parse_func
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Pipeline
from kevin_dl.workers.variable import DATASETS


@DATASETS.register(name=":adjuster:Mixup_Adjuster")
class Mixup_Adjuster(Dataset):
    """
        对给定数据集中的数据按照 mixup 算法进行混合构造出一个新的数据集

        工作流程：
            alpha, mixed_ratio, mixed_batch_size, b_idd_lam_in_batch ==> shuffled_idx_ls, lam_ls
                                                                                      ||
                                                                                      V
            src_dataset, idx ==> data ==> preprocessor ==> x_fetcher, y_fetcher ==> x_mixed, y_mixed

        支持通过 push_update_to_group_space() 来同步同一分组下不同实例的设置。
    """
    # 全局 Manager，所有 SharedDict 实例共享同一个 manager
    _manager = mp.Manager()

    # 共享的 dict proxy 和 Lock
    _share_dict = _manager.dict()
    _lock = _manager.Lock()

    def __init__(self, **kwargs):
        """
            参数：
                src_dataset:                    <Dataset> 原始数据集。
                preprocessor:                   <callable/str> 在获取数据后，对数据进行预处理
                                                    当为函数时，要求形如 func(data) ==> data_ ，其返回数据将会用于下游的 mix 处理等。
                                                    当为 str 时，要求其以 <eval> 起始，并可解释为函数。
                x_fetcher:                      <str/dict/list of str or dict> 指定数据中的模型输入部分
                                                    当输入为 dict 时，要求具有以下键值对：
                                                        - name：         <str> 该部分在数据中的位置，
                                                                        请参考 kevin_toolbox.nested_dict_list 中的介绍。
                                                    当输入为 str 时，等效于下面形式的输入：
                                                        {"name": x_fetcher}
                                                    当输入为 list，表示需要分别对多个输入进行混合。
                y_fetcher:                      <str/dict/list of str or dict> 指定数据中的标签部分
                                                    当输入为 dict 时，要求具有以下键值对：
                                                        - name:                     <str>
                                                        - b_need_onehot:(可选)        <boolean> 当数据为单个整数时，是否将其转换为 onehot 形式。
                                                                                        默认为 False。
                                                        - num_classes:(可选)          <int> 如果需要转为 onehot 形式，其维度应该是多少。
                alpha:                          <float> (0,+infty) 混合比例系数的采样分布 beta 分布的超参数。
                                                    默认为 1.0。
                mixing_method_for_x:            <dict> 对 x 的混合方式。
                                                    一个形如 {"type_": <str>, ...} 的字典
                                                    type_ 可选值：
                                                        - "mixup":      对应mixup论文中的方式。
                                                        - "gixup":      考虑到伽马变换的影响，先进行伽马逆变换到光强空间，再进行线性混合。
                                                    当 type_ 设定为 "gixup" 时，可以进一步设置以下参数：
                                                        - gamma             伽马值
                                                                                默认为 2.0
                mixed_ratio:                    <float> 进行混合的数据占比。
                                                    默认为 1.0，亦即所有数据都参与混合。
                mixed_batch_size:               <int> 混合时以多少数据为一个batch进行打乱。
                                                    在进行混合时，将会以 batch 为单位，在每个 batch 内部对数据进行打断和混合。
                                                    默认为 -1，表示将整个数据集看做一个 batch，亦即 batch size == dataset size
                b_idd_lam_in_batch:             <boolean> 对于 batch 内的每个数据，其 lam 系数是否是独立采样。
                                                    默认为 True。
                group_name:                     <boolean> 分组名。
                                                    同一分组内的各个实例（即使位于不同进程中），都将共享所在分组名下的对应的内存空间。
                                                    共享的内容包括：
                                                        - check_flag:   <int> 当实例自身的 self.check_flag 和分组的不一致时，将会强行使用分组的 paras 字段
                                                                        中的内容来更新实例自身的 self.paras 并重新生成 self.shuffled_index 等。
                                                                注意！！利用该特性，可以通过分组中的某个实例来控制其余的所有实例的更新，即使这些其他实例位于不同的集成
                                                                （比如dataloader中num_processes>1时将会复制实例）。
                                                        - paras:        分组共享的参数。
                                                                注意！！ 以下参数并不保存到共享空间，因此无法通过共享空间进行同步修改：
                                                                    - preprocessor
                                                                    - src_dataset
                                                                    - x_transform
                                                                    - y_transform
                                                    默认为 None。
                x_transform:                    <dict of Pipeline or paras> 对数据中的模型输入部分进行的变换。
                                                    以 x_fetcher 为键，值为其所对应的变换。
                                                    若值为 dict 则使用 Pipeline() 进行构建。
                                                    默认为 None，不使用。
                y_transform:                    <dict of Pipeline or paras> 对数据中的标签部分进行的变换。
                                                    设置方式同上。
                b_do_x/y_transform_before_mix:  <boolean> 是否在混合前就对输入/标签进行变换。
                                                    默认为 False，表示对混合后的变量再施加变换。
                seed:                           <int> 设定随机发生器
                task_type:                      <str> 任务类型，有 "train" "test" "val" 可选
                                                    该参数仅在 x_transform 和 y_transform 非空时起效，当设置为 "train" 时，每次调用
                                                        x_transform 或 y_transform 进行扰动时都是随机的，即使 idx 一样也可能不同，当设置为其他
                                                        时 x_transform 和 y_transform 中的随机种子将在每次调用前被设置为 idx+seed，以保证
                                                        相同 idx 下生成的扰动是相同的。
                                                    注意，该参数对 shuffled_idx_ls, lam_ls 并无任何影响，因此如果要实现 shuffled_idx_ls, lam_ls
                                                        也随着 epoch 而变化的效果，请通过调整实例的 seed，并使用 push_update_to_group_space() 将改动推送
                                                        到所有副本中。
                                                    默认为 "train"。
        """
        super().__init__()

        # 默认参数
        paras = {
            # 原始数据集
            "src_dataset": None,
            "preprocessor": None,
            "x_fetcher": None,
            "y_fetcher": None,
            # 目标数据集
            "alpha": 1.0,
            "mixing_method_for_x": {"type_": "mixup"},
            "mixed_ratio": 1.0,
            "mixed_batch_size": None,
            "b_idd_lam_in_batch": True,
            #
            "group_name": None,
            #
            "x_transform": None,
            "y_transform": None,
            "b_do_x_transform_before_mix": False,
            "b_do_y_transform_before_mix": False,
            #
            "seed": None,
            "task_type": "train",
        }

        # 获取参数
        paras.update(kwargs)

        # 校验参数
        #   alpha
        assert isinstance(paras["alpha"], (int, float)) or paras["alpha"] is None
        if paras["alpha"] is None or paras["alpha"] < 0:
            paras["alpha"] = None
        else:
            assert 0 < paras["alpha"]
        assert paras["mixing_method_for_x"]["type_"] in ["mixup", "gixup"]
        #
        assert isinstance(paras["mixed_ratio"], (float, int)) and 0.0 <= paras["mixed_ratio"] <= 1.0
        if paras["mixed_batch_size"] is not None and paras["mixed_batch_size"] < 0:
            paras["mixed_batch_size"] = None
        #
        assert isinstance(paras["src_dataset"], (Dataset,))
        self.src_dataset = paras.pop("src_dataset")
        self.preprocessor = paras.pop("preprocessor")
        if self.preprocessor is not None:
            self.preprocessor = parse_func(self.preprocessor)
        for k in ["x_fetcher", "y_fetcher"]:
            if paras[k] is None:
                continue
            if not isinstance(paras[k], (list, tuple)):
                paras[k] = [paras[k]]
            temp = []
            for i in paras[k]:
                if isinstance(i, str):
                    i = {"name": i}
                assert isinstance(i, dict)
                if k == "y_fetcher":
                    i.setdefault("b_need_onehot", False)
                    if i["b_need_onehot"]:
                        assert "num_classes" in i
                temp.append(i)
            paras[k] = temp
        #
        for k in paras.keys():
            if (k.startswith("x_transform") and k != "x_transform") or (
                    k.startswith("y_transform") and k != "y_transform"):
                warnings.warn(f"wrong parameter {k}, did you mean x_transform or y_transform")
        self.transform_s = {"x": paras.pop("x_transform"), "y": paras.pop("y_transform")}
        for name, it in self.transform_s.items():
            if it is not None:
                for k in it.keys():
                    if isinstance(it[k], dict):
                        if name == "x":
                            it[k].setdefault("mapping_ls_for_inputs", ["image"])
                            it[k].setdefault("mapping_ls_for_outputs", "image")
                        it[k] = Pipeline(**it[k])
                    assert isinstance(it[k], Pipeline)

        # 建立 shuffled_idx_ls, lam_ls
        self.shuffled_idx_ls, self.lam_ls = self._generate_shuffled_idx_and_lam(
            mixed_ratio=paras["mixed_ratio"], mixed_batch_size=paras["mixed_batch_size"],
            b_idd_lam_in_batch=paras["b_idd_lam_in_batch"], dataset_size=len(self.src_dataset),
            seed=paras["seed"], alpha=paras["alpha"]
        )

        self.paras = paras

        self.check_flag = self.get_shared_dict(key="check_flag", default=0)
        self.set_shared_dict(key="check_flag", value=self.check_flag)
        self.set_shared_dict(key="paras", value=ndl.copy_(var=self.paras, b_deepcopy=True))

    def set_shared_dict(self, key, value, **kwargs):
        """
            向共享 dict 中写入 value
        """
        group_name = kwargs.get("group_name", self.paras["group_name"])
        if group_name != self.paras["group_name"]:
            warnings.warn(f'you are writing to a different group {group_name},'
                          f' while the current group is {self.paras["group_name"]}')
        with Mixup_Adjuster._lock:
            if group_name not in Mixup_Adjuster._share_dict:
                # 创建二级共享字典
                Mixup_Adjuster._share_dict[group_name] = Mixup_Adjuster._manager.dict()
            # 直接访问二级字典的代理对象
            group_dict = Mixup_Adjuster._share_dict[group_name]
            group_dict[key] = value

    def get_shared_dict(self, key, **kwargs):
        """
            从共享 dict 中读取 value
        """
        group_name = kwargs.get("group_name", self.paras["group_name"])
        with Mixup_Adjuster._lock:
            if group_name in Mixup_Adjuster._share_dict:
                group_dict = Mixup_Adjuster._share_dict[group_name]
                if "default" in kwargs:
                    return group_dict.get(key, kwargs["default"])
                elif key in group_dict:
                    return group_dict[key]
            elif "default" in kwargs:
                return kwargs["default"]
            else:
                raise KeyError(f"{group_name} not in Mixup_Adjuster._share_dict")

    def push_update_to_group_space(self, **kwargs):
        """
            将共享 dict 中对应分组的 check_flag 加一，并将当前实例的 paras 推送到共享空间，
                从而引导在调用 __getitem__() 时重新生成 shuffled_idx 和 lam
        """
        group_name = kwargs.get("group_name", self.paras["group_name"])
        check_flag = self.get_shared_dict(key="check_flag", group_name=group_name)
        self.set_shared_dict(key="check_flag", value=check_flag + 1, group_name=group_name)
        self.set_shared_dict(key="paras", value=ndl.copy_(var=self.paras, b_deepcopy=True), group_name=group_name)

    @staticmethod
    def _generate_shuffled_idx_and_lam(mixed_ratio, mixed_batch_size, b_idd_lam_in_batch, dataset_size, seed, alpha):
        shuffled_idx_ls = [None] * dataset_size
        lam_ls = [None] * dataset_size
        if alpha is None:
            return shuffled_idx_ls, lam_ls
        #
        mixed_batch_size = dataset_size if mixed_batch_size is None else mixed_batch_size
        rng = get_rng(seed=seed)
        idx_ls = list(range(dataset_size))
        rng.shuffle(idx_ls)
        idx_ls = idx_ls[:math.ceil(dataset_size * mixed_ratio)]
        for idx_batch in chunk_generator(idx_ls, chunk_size=mixed_batch_size, b_drop_last=False,
                                         b_display_progress=False):
            idx_batch = np.asarray(idx_batch)
            # 生成随机 pairs
            p_ = rng.permutation(len(idx_batch))
            # 生成 lam
            if b_idd_lam_in_batch:
                lam_ = [rng.beta(alpha, alpha) for _ in range(len(idx_batch))]
            else:
                lam_ = rng.beta(alpha, alpha)
                lam_ = [lam_] * len(idx_batch)
            #
            for i, j, k in zip(idx_batch, np.asarray(idx_batch)[p_], lam_):
                shuffled_idx_ls[i] = j
                lam_ls[i] = k
        return shuffled_idx_ls, lam_ls

    @staticmethod
    def _mixup(data_0, data_1, x_fetcher_ls, y_fetcher_ls, lam, mixing_method_for_x, x_transform=None, y_transform=None,
               b_do_x_transform_before_mix=False, b_do_y_transform_before_mix=False):
        data = ndl.copy_(var=data_0, b_deepcopy=False)

        # 计算 x_mixed
        if x_fetcher_ls is not None:
            for fetcher in x_fetcher_ls:
                x_0 = ndl.get_value(var=data_0, name=fetcher["name"])
                x_1 = ndl.get_value(var=data_1, name=fetcher["name"])
                if b_do_x_transform_before_mix and x_transform is not None and fetcher["name"] in x_transform:
                    x_0 = x_transform[fetcher["name"]](x_0)
                    x_1 = x_transform[fetcher["name"]](x_1)
                if mixing_method_for_x["type_"] == "mixup":
                    x_mixed = lam * x_0 + (1 - lam) * x_1
                else:  # "gixup"
                    gamma = mixing_method_for_x.get("gamma", 2.0)
                    assert gamma > 0
                    if not torch.is_tensor(x_0):
                        x_0 = torch.as_tensor(x_0, dtype=torch.float64)
                    if not torch.is_tensor(x_1):
                        x_1 = torch.as_tensor(x_1, dtype=torch.float64)
                    #
                    if not bool(torch.all(x_0 >= -1e-6)) or not bool(torch.all(x_1 >= -1e-6)):
                        warnings.warn(f"from Mixup_Pro:\n\tx_raw has negative values, "
                                      f"which may cause problems in gamma space.")
                    x_0.clamp_(min=0)
                    x_1.clamp_(min=0)
                    # 首先进行逆 gamma 变换，然后再在 linear 空间中进行线性组合，最后再进行 gamma 变换
                    x_0 = x_0 ** gamma
                    x_1 = x_1 ** gamma
                    x_mixed = lam * x_0 + (1 - lam) * x_1
                    x_mixed = x_mixed ** (1 / gamma)
                if (not b_do_x_transform_before_mix) and x_transform is not None and fetcher["name"] in x_transform:
                    x_mixed = x_transform[fetcher["name"]](x_mixed)
                data = ndl.set_value(var=data, name=fetcher["name"], value=x_mixed, b_force=False)

        # 计算 y_mixed
        if y_fetcher_ls is not None:
            for fetcher in y_fetcher_ls:
                temp = []
                for data_ in [data_0, data_1]:
                    y = ndl.get_value(var=data_, name=fetcher["name"])
                    if b_do_y_transform_before_mix and y_transform is not None and fetcher["name"] in y_transform:
                        y = y_transform[fetcher["name"]](y)
                    if fetcher["b_need_onehot"]:  # 对于分类任务，需要先将y转换为onehot向量，再进行差插值
                        y_ = torch.as_tensor(y).long()
                        if len(y_.shape) == 0:
                            y = torch.nn.functional.one_hot(y_.view(-1), fetcher["num_classes"])[0]
                        elif y_.shape[-1] != fetcher["num_classes"]:
                            y = torch.nn.functional.one_hot(y_, fetcher["num_classes"])
                    temp.append(y)
                y_0, y_1 = temp
                y_mixed = lam * y_0 + (1 - lam) * y_1
                if (not b_do_y_transform_before_mix) and y_transform is not None and fetcher["name"] in y_transform:
                    y_mixed = y_transform[fetcher["name"]](y_mixed)
                data = ndl.set_value(var=data, name=fetcher["name"], value=y_mixed, b_force=False)

        return data

    @staticmethod
    def _wto_mixup(data, x_fetcher_ls, y_fetcher_ls, x_transform=None, y_transform=None):
        if x_fetcher_ls is not None:
            for fetcher in x_fetcher_ls:
                x = ndl.get_value(var=data, name=fetcher["name"])
                if x_transform is not None and fetcher["name"] in x_transform:
                    x = x_transform[fetcher["name"]](x)
                data = ndl.set_value(var=data, name=fetcher["name"], value=x, b_force=False)
        if y_fetcher_ls is not None:
            for fetcher in y_fetcher_ls:
                y = ndl.get_value(var=data, name=fetcher["name"])
                if fetcher["b_need_onehot"]:  # 对于分类任务，需要先将y转换为onehot向量，再进行差插值
                    y_ = torch.as_tensor(y).long()
                    if len(y_.shape) == 0:
                        y = torch.nn.functional.one_hot(y_.view(-1), fetcher["num_classes"])[0]
                    elif y_.shape[-1] != fetcher["num_classes"]:
                        y = torch.nn.functional.one_hot(y_, fetcher["num_classes"])
                    y = 1.0 * y
                if y_transform is not None and fetcher["name"] in y_transform:
                    y = y_transform[fetcher["name"]](y)
                data = ndl.set_value(var=data, name=fetcher["name"], value=y, b_force=False)
        return data

    def __len__(self):
        return len(self.src_dataset)

    def __getitem__(self, idx):
        if Task_Type(self.paras["task_type"]) is not Task_Type.Train:
            for pipeline in [self.transform_s["x"], self.transform_s["y"]]:
                if pipeline is not None:
                    for v in pipeline.values():
                        v.set_rng(seed=self.paras["seed"] + idx if self.paras["seed"] is not None else idx,
                                  b_delayed_set_rng=False, b_seed_wrt_worker_id=False)
        # check and regenerate
        check_flag = self.get_shared_dict(key="check_flag")
        if self.check_flag != check_flag:
            self.paras = self.get_shared_dict(key="paras")
            self.check_flag = check_flag
            self.shuffled_idx_ls, self.lam_ls = self._generate_shuffled_idx_and_lam(
                mixed_ratio=self.paras["mixed_ratio"], mixed_batch_size=self.paras["mixed_batch_size"],
                b_idd_lam_in_batch=self.paras["b_idd_lam_in_batch"], dataset_size=len(self.src_dataset),
                seed=self.paras["seed"], alpha=self.paras["alpha"]
            )
        #
        data_0 = self.src_dataset[idx]
        data_0 = data_0 if self.preprocessor is None else self.preprocessor(data_0)
        if self.shuffled_idx_ls[idx] is None or self.lam_ls[idx] is None:
            res = self._wto_mixup(data=data_0, x_fetcher_ls=self.paras["x_fetcher"],
                                  y_fetcher_ls=self.paras["y_fetcher"], x_transform=self.transform_s["x"],
                                  y_transform=self.transform_s["y"])
        else:
            data_1 = self.src_dataset[self.shuffled_idx_ls[idx]]
            data_1 = data_1 if self.preprocessor is None else self.preprocessor(data_1)
            res = self._mixup(data_0=data_0, data_1=data_1, x_fetcher_ls=self.paras["x_fetcher"],
                              y_fetcher_ls=self.paras["y_fetcher"], lam=self.lam_ls[idx],
                              mixing_method_for_x=self.paras["mixing_method_for_x"],
                              x_transform=self.transform_s["x"], y_transform=self.transform_s["y"],
                              b_do_x_transform_before_mix=self.paras["b_do_x_transform_before_mix"],
                              b_do_y_transform_before_mix=self.paras["b_do_y_transform_before_mix"])
        return res

    # --------------------------- 辅助功能 --------------------------- #

    def read_statistics(self):
        temp = np.asarray([i for i in self.lam_ls if i is not None])
        if len(temp) > 0:
            bins = np.linspace(0, 1, 21)  # [0.0, 0.1, ..., 1.0]
            bins[0] -= 1e-2
            bins[1] += 1e-2
            counts, bin_edges = np.histogram(temp, bins=bins)
            return {"lam": dict(counts=counts.tolist(), bin_edges=bin_edges.tolist(),
                                mean=np.mean(temp), std=np.std(temp), max=np.max(temp), min=np.min(temp))}
        else:
            return {"lam": dict(counts=[], bin_edges=[], mean=None, std=None, max=None, min=None)}

    @property
    def statistics(self):
        return self.read_statistics()


if __name__ == "__main__":
    import copy
    from kevin_dl.workers.datasets.cv.torchvision_ import Build_Torchvision_Dataset
    from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format

    a = Build_Torchvision_Dataset(dataset_name="CIFAR10")(
        root='~/data', train=True, download=True,
        transform={
            "settings": [
                # {
                #     "name": ":for_images:torchvision:RandomCrop",
                #     "paras": {
                #         "size": 32,
                #         "padding": 4
                #     }
                # },
                # {
                #     "name": ":for_images:torchvision:RandomHorizontalFlip",
                #     "paras": {
                #         "p": 0.5
                #     }
                # },
                {
                    "name": ":for_images:torchvision:ToTensor",
                    "paras": {}
                },
                # {
                #     "name": ":for_images:torchvision:Normalize",
                #     "paras": {
                #         "mean": (0.4914, 0.4822, 0.4465),
                #         "std": (0.2023, 0.1994, 0.201)
                #     }
                # }
            ]
        },
        seed=114514
    )
    print(a[0])

    b = Mixup_Adjuster(
        src_dataset=a,
        preprocessor="<eval>lambda x: list(x)",
        x_fetcher="@0", y_fetcher={"name": "@1", "b_need_onehot": True, "num_classes": 10},
        x_transform={
            "@0": {
                "settings": [
                    {
                        "name": ":for_images:torchvision:RandomCrop",
                        "paras": {
                            "size": 32,
                            "padding": 4
                        }
                    },
                    {
                        "name": ":for_images:torchvision:RandomHorizontalFlip",
                        "paras": {
                            "p": 0.99
                        }
                    },
                    # {
                    #     "name": ":for_images:torchvision:Normalize",
                    #     "paras": {
                    #         "mean": (0.4914, 0.4822, 0.4465),
                    #         "std": (0.2023, 0.1994, 0.201)
                    #     }
                    # }
                ]
            }
        },
        y_transform=None,
        alpha=1.0,
        mixing_method_for_x={"type_": "gixup", "gamma": 2.2},
        mixed_ratio=0.1,
        mixed_batch_size=100,
        b_idd_lam_in_batch=False,
        # group_name="here",
        seed=1919810
    )
    print(b[0])
    print(len(b))

    # 验证是否有正常混合
    print(b.shuffled_idx_ls[0], b.lam_ls[0])  # 41449, 0.18560000824296494
    convert_format(image=a[0][0], output_format=Image_Format.PIL_IMAGE).show()
    convert_format(image=a[41449][0], output_format=Image_Format.PIL_IMAGE).show()
    convert_format(image=b[0][0], output_format=Image_Format.PIL_IMAGE).show()
    print(b.statistics)

    # 验证是否能正常同步
    c = copy.deepcopy(b)
    c.paras["seed"] = 12345
    c.push_update_to_group_space()
    _ = b[1]
    _ = c[1]
    print(b.shuffled_idx_ls[0], b.lam_ls[0])  # 14299, 0.411035616567533
    print(c.shuffled_idx_ls[0], c.lam_ls[0])  # 14299, 0.411035616567533
    print(b[1])
    print(b.statistics)
