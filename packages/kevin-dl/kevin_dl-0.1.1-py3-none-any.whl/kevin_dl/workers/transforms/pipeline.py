import numpy as np
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.patches.for_numpy.random import get_rng
from kevin_dl.utils import reorganize_by_mapping


def get_worker_id():
    from torch.utils.data import get_worker_info
    worker_info = get_worker_info()
    wid = worker_info.id if worker_info is not None else 0
    return wid


def map_to_dict(mapping_ls, args, kwargs):
    """
        主要为了实现 Pipeline 中 mapping_ls_for_inputs 参数对应功能
    """
    if not mapping_ls:
        return args, kwargs

    has_default_value_ls = [isinstance(i, (tuple, list,)) for i in mapping_ls]

    out_s = dict()
    for it, arg, b_has_default in zip(mapping_ls, args, has_default_value_ls):
        key = it[0] if b_has_default else it
        out_s[key] = arg
    for it, b_has_default in zip(mapping_ls[len(args):], has_default_value_ls[len(args):]):
        key = it[0] if b_has_default else it
        if b_has_default:
            v = kwargs.get(key, it[1])
        else:
            assert key in kwargs, f"Missing required parameters {key}"
            v = kwargs[key]
        out_s[key] = v
    return [], {"input_s": out_s}


def map_to_list(mapping_ls, res_s):
    """
        主要为了实现 Pipeline 中 mapping_ls_for_outputs 参数对应功能
    """
    if not mapping_ls:
        return res_s

    b_should_unpack = not isinstance(mapping_ls, (tuple, list,))
    if b_should_unpack:
        mapping_ls = [mapping_ls]

    out_ls = []
    for it in mapping_ls:
        if isinstance(it, (tuple, list,)):
            v = res_s.get(it[0], it[1])
        else:
            assert it in res_s, f"Missing required key {it}"
            v = res_s[it]
        out_ls.append(v)

    return out_ls[0] if b_should_unpack else out_ls


class Pipeline:

    def __init__(self, **kwargs):
        """
            参数：
                settings:               <list of setting> 各个组件的设置
                drop_prob:              <list of floats/str> 按概率“逐一”对各个组件判断是否丢弃
                                            比如对于 settings = [1, 2, 3, 4], drop_prob = [0.1, 0.9, 0.8, 0.3]
                                                处理后可能得到 pipeline = [1, 4]
                                            默认为 None，表示不进行丢弃
                pick_prob:              <list of floats/str> 按概率从多个组件中选出“一个”
                                            比如对于 settings = [1, 2, 3, 4], pick_prob = [0.1, 0.9, 0.8, 0.3]
                                                处理后可能得到 pipeline = [2]
                                            默认为 None，表示不进行挑选
                order_prob:             <list of floats/str> 按概率对组件进行排序，概率越大意味着排序可能越高
                                            比如对于 settings = [1, 2, 3, 4], order_prob = [0.1, 0.9, 0.8, 0.3]
                                                处理后可能得到 pipeline = [2, 3, 4, 1]
                                            默认为 None，表示按原始顺序
                        对于每次调用 pipeline，将会按如下顺序处理：
                            settings ==> drop_prob ==> pick_prob/order_prob ==> build pipeline
                        其中 pick_prob 和 order_prob 由于逻辑关系只能二选一起效，同时设置时以前者为准。
                        这些 prob 参数除了支持离散概率外，也支持以下概率分布：
                            - "uniform"
                        以上概率将会进行自动的归一化

                b_include_details:      <boolean> 是否将详细处理信息也添加到输出的"details_ls"字段中
                seed:                   <int> 随机种子
                rng:                    <Random Generator> 给定的随机采样器
                        注意：
                            - seed 和 rng 二选一
                            - b_include_details、seed 和 rng 三个参数当设置为非 None 值时，将覆盖组件中原有的设置。
                                默认为 True。
                mapping_ls_for_inputs:  <list/tuple of mapping> 对输入进行的映射。
                                            默认为 None，不进行映射。
                                                此时 self.__call__() 只能接受一个 <dict> 类型的 input_s 作为输入。
                                            当有设置时，将 self.__call__(*args, **kwargs) 中的一系列输入根据 mapping_ls_for_inputs 映射成
                                                一个 input_s 作为输入。
                                            mapping 有两种输入格式：
                                                1. 比如当 mapping_ls_for_inputs=[
                                                        {
                                                            "src": (":args@0", ":kwargs:image"),  # image 参数
                                                            "dst": ":args@0:image"
                                                        },
                                                        {
                                                            "src": (":args@1", ":kwargs:b_blur"),  # b_blur 参数
                                                            "dst": ":args@0:b_blur"
                                                        },
                                                        {
                                                            "src": (":args@2", ":kwargs:seed"),  # seed 参数
                                                            "dst": ":args@0:seed",
                                                            "default": 114514
                                                        }
                                                    ] 时，
                                                2. 或者比如当 mapping_ls_for_inputs=[
                                                    "image", "b_blur", ("seed", 114514)
                                                    ] 时,
                                                （！！建议使用第二种方式，更加简便，且运行速度更快）

                                                对于 self.__call__(x,b_blur=True) 或者 self.__call__(x,True)，将等效于：
                                                    input_s={"image":x, "b_blur":True, "seed":114514}  # "seed" 因为未指定而使用默认值。
                                                对于 self.__call__(x) 将因为缺少必要参数 b_blur 而报错。
                mapping_ls_for_outputs: <list/tuple/single of mapping> 对输出的映射。
                                            默认为 None，不进行映射。
                                                此时 self.__call__() 返回一个 <dict> 类型的 res_s 作为输出。
                                            当设置为 list/tuple 时，将输出的 res_s 映射为对应值进行输出。
                        ps：
                            - 合理利用 mapping_ls_for_inputs 和 mapping_ls_for_outputs 参数可以将 pipeline 变为 torch.transform 兼容的形式。
                b_delayed_set_rng:      <boolean> 延迟更新 rng。
                b_seed_wrt_worker_id:   <boolean> 在多进程中，实际设定的随机种子 seed 是否应该等于 seed + worker id。
                        上面两个参数的解释可参看 set_rng() 中的介绍。
                        这两个参数仅在实例初始化阶段起效一次，且可以通过 set_rng() 来进行覆盖。
        """
        # 默认参数
        paras = {
            # 必要参数
            "settings": None,
            #
            "drop_prob": None,
            "pick_prob": None,
            "order_prob": None,
            "seed": None,
            "rng": None,
            "replay_times": None,
            "b_include_details": True,
            #
            "mapping_ls_for_inputs": None,
            "mapping_ls_for_outputs": None,
            #
            "b_delayed_set_rng": True,
            "b_seed_wrt_worker_id": True
        }

        # 获取参数
        paras.update(ndl.copy_(var=kwargs, b_deepcopy=True))

        # 校验参数
        assert isinstance(paras["settings"], (list,))
        for k in paras.keys():
            if k.endswith("prob") and paras[k] is not None:
                if paras[k] == "uniform":
                    paras[k] = np.ones(len(paras["settings"])) / len(paras["settings"])
                assert len(paras[k]) == len(paras["settings"])
                paras[k] = np.asarray(paras[k])
                # 对概率进行归一化
                if k == "drop_prob":
                    paras[k] = np.clip(paras[k], 0, 1)
                else:
                    paras[k] /= np.sum(paras[k])

        for i in paras["settings"]:
            i.setdefault("paras", dict())
            i["paras"]["b_include_details"] = paras["b_include_details"]

        # 根据 settings 构建组件
        from kevin_dl.workers.variable import TRANSFORMS

        self.components = [TRANSFORMS.get(name=i["name"])(**i["paras"]) for i in paras["settings"]]
        self.rng = None
        self._state_s = dict(b_delayed_set_rng=None, set_rng_paras=dict())
        self.set_rng(seed=paras["seed"], rng=paras["rng"],
                     b_delayed_set_rng=paras["b_delayed_set_rng"], b_seed_wrt_worker_id=paras["b_seed_wrt_worker_id"])
        self.__replay_times = None
        self.replay_last_process(replay_times=paras["replay_times"])

        self.paras = paras
        self.__last_idx_ls = None

    def set_rng(self, seed=None, rng=None, b_delayed_set_rng=True, b_seed_wrt_worker_id=True):
        """
            设定/重新设定随机采样器

            参数：
                seed:                   <int> 随机种子
                rng:                    <Random Generator> 给定的随机采样器
                                以上参数二选一
                b_delayed_set_rng:      <boolean> 延迟更新。
                                            是否在后续调用 __call__() 时，才进行 rng 的设定。
                b_seed_wrt_worker_id:   <boolean> 在多进程中，实际设定的随机种子 seed 是否应该等于 seed + worker id。
                                上面两个参数的作用是什么？
                                    1. 对于训练阶段，若 DataLoader 使用多进程加载数据（num_workers > 1），其会为每个 worker 都构造一份 Dataset 副本，
                                        如果 Dataset 的属性有包含 Pipeline 的实例，那么也会递归地为 Pipeline 的实例构造副本。
                                        当 seed != None 时，使用的不是全局随机器，而是单独构造的随机器实例，该实例也会随之被构造副本，此时就会导致避免多个进程的
                                        随机器状态重复。
                                        此时我们可以通过令 b_update_at_first_call=True, b_seed_wrt_worker_id=True 来保证不同进程中的副本能使用不同的随机器，
                                        避免多个进程的随机器状态重复。具体可以参看《Dataloader多进程复制问题》。特别地，当 seed=None，使用的是全局随机器，此时不会因为副本
                                    2. 对于测试阶段，如果我们需要让随机器的状态由数据的 idx 确定，以保证每次测试的随机数序列都是相同的，那么一般在 Dataset 的
                                        __call__ 中通过 Pipeline.set_rng(seed=idx, b_update_at_first_call=False, b_seed_wrt_worker_id=False)
                                        来设定。
        """
        self._state_s["b_delayed_set_rng"] = b_delayed_set_rng
        if b_delayed_set_rng:
            self._state_s["set_rng_paras"].update(dict(seed=seed, rng=rng, b_seed_wrt_worker_id=b_seed_wrt_worker_id,
                                                       b_delayed_set_rng=False))
            return
        if seed is not None and b_seed_wrt_worker_id:
            seed = seed + get_worker_id()
        self.rng = get_rng(seed=seed, rng=rng)
        for i in self.components:
            i.set_rng(rng=self.rng)

    def determine_pipeline_by_prob(self):
        idx_ls = np.arange(len(self.paras["settings"]))

        # drop independently
        if self.paras["drop_prob"] is not None:
            drop_ls = self.rng.random(len(idx_ls)) > self.paras["drop_prob"]
            idx_ls = idx_ls[drop_ls]
        else:
            drop_ls = None
        # pick one /determine order
        if len(idx_ls) > 1:
            p = self.paras["pick_prob"] if self.paras["pick_prob"] is not None else self.paras["order_prob"]
            keep_nums = 1 if self.paras["pick_prob"] is not None else len(idx_ls)
            if p is not None:
                if drop_ls is not None:
                    p = p[drop_ls]
                    p /= np.sum(p)
                idx_ls = self.rng.choice(idx_ls, keep_nums, replace=False, p=p)

        return idx_ls

    def __call__(self, *args, **kwargs):
        """
            使用时调用该函数
        """
        if self._state_s["b_delayed_set_rng"]:
            self.set_rng(**self._state_s["set_rng_paras"])
        # 输入参数处理
        mapping_ls = self.paras["mapping_ls_for_inputs"]
        if mapping_ls is not None:
            if len(mapping_ls) > 0 and isinstance(mapping_ls[0], (dict,)):
                # 方式1，调用 reorganize_by_mapping() 来解释
                input_s = reorganize_by_mapping(var=dict(args=args, kwargs=kwargs), mapping_ls=mapping_ls)
            else:
                # 方式2，调用 map_to_dict() 进行解释
                input_s = map_to_dict(mapping_ls=mapping_ls, args=args, kwargs=kwargs)[1]["input_s"]
        else:
            input_s = kwargs["input_s"] if "input_s" in kwargs else args[0]

        # 随机选择 component
        if self.__replay_times == 0 or self.__last_idx_ls is None:
            idx_ls = self.determine_pipeline_by_prob()
            self.__last_idx_ls = idx_ls
        else:
            idx_ls = self.__last_idx_ls
            self.__replay_times = self.__replay_times if self.__replay_times < 0 else self.__replay_times - 1

        components = [self.components[idx] for idx in idx_ls]
        res = self.cal(input_s, components)

        # 最后要对 components 中的 __replay_times 进行同步（包含暂时未被调用的组件），以免这次未被调用的组件在本次重播结束后又被重播多次。
        self.replay_last_process(replay_times=self.__replay_times)

        # 输出处理
        mapping_ls = self.paras["mapping_ls_for_outputs"]
        if mapping_ls is not None:
            if len(mapping_ls) > 0 and isinstance(mapping_ls[0], (dict,)):
                # 方式1，调用 reorganize_by_mapping() 来解释
                res = reorganize_by_mapping(var=res, mapping_ls=mapping_ls)
            else:
                # 方式2，调用 map_to_dict() 进行解释
                res = map_to_list(mapping_ls=mapping_ls, res_s=res)

        return res

    def cal(self, input_s: dict, components, **kwargs) -> dict:
        for component in components:
            input_s = component(input_s)
        return input_s

    def replay_last_process(self, replay_times=None):
        """
            重播最近一次的处理（保持 self.cal() 中 kwargs 不变）

            参数：
                replay_times:       <int/None> 重播多少次
                                        可选值：
                                            - None,0 : 不进行重播
                                            - 大于 0 的整数 n: 在之后 n 次调用中进行重播
                                            - 小于 0 的整数 n: 进行无限次重播
                                        默认为 None。
        """
        replay_times = 0 if replay_times is None else replay_times
        assert isinstance(replay_times, (int,))

        for i in self.components:
            i.replay_last_process(replay_times=replay_times)
        self.__replay_times = replay_times

    def state_dict(self):
        """
            获取状态
                （该方法有待完善，暂不建议使用）
        """
        return ndl.copy_(var={"replay_times": self.__replay_times, "last_idx_ls": self.__last_idx_ls}, b_deepcopy=True,
                         b_keep_internal_references=True)


if __name__ == '__main__':
    settings_ = [
        {
            "name": ':for_images:blur:Gaussian_Blur',
            "paras": {
                "sigma": {
                    "p_type": "float",
                    "p_prob": "uniform",
                    "high": 10,
                    "low": 0,
                }
            }
        },
        {
            "name": ':for_images:color:Brightness_Shift',
            "paras": {
                "beta": {
                    "p_type": "float",
                    "p_prob": "uniform",
                    "high": 0.2,
                    "low": -0.2,
                }
            }
        },
        {
            "name": ':for_images:blur:Motion_Blur',
            "paras": {
                "kernel_size": {
                    "p_type": "categorical",
                    "choices": [1, 2, 4, 8, 16]
                },
                "angle": {
                    "p_type": "int",
                    "p_prob": "uniform",
                    "high": 180,
                    "low": 0,
                }
            }
        }
    ]
    pp = Pipeline(settings=settings_, drop_prob=[0.2, 0.2, 0.2], order_prob=[0.5, 0.5, 0.5], b_include_details=True)
    pp.set_rng(seed=114514, b_delayed_set_rng=False)

    # settings_ = [
    #     {
    #         "name": ':for_images:blur:Gaussian_Blur',
    #         "paras": {
    #             "sigma": 0.36828474466200967
    #         }
    #     },
    #     {
    #         "name": ':for_images:color:Brightness_Shift',
    #         "paras": {
    #             "beta": 0.5
    #         }
    #     },
    #     {
    #         "name": ':for_images:blur:Motion_Blur',
    #         "paras": {
    #             "kernel_size": 16,
    #             "angle": 153
    #         }
    #     }
    # ]
    # pp = Pipeline(settings=settings_, b_include_details=True)

    print(pp.determine_pipeline_by_prob())

    import os
    from PIL import Image
    from kevin_dl.utils.variable import root_dir
    from kevin_dl.workers.transforms.for_images.utils import get_format, convert_format, Image_Format

    image = Image.open(
        os.path.join(root_dir,
                     "kevin_dl/workers/transforms/for_images/test/test_data/data_0/ILSVRC2012_val_00040001.JPEG"))

    output_s = pp(input_s=dict(image=image))
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
