from abc import ABC, abstractmethod
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.patches.for_numpy.random import get_rng
from kevin_dl.utils import sample_from_feasible_domain


class Base_Transform(ABC):

    def __init__(self, b_include_details=True, seed=None, rng=None, replay_times=None, **kwargs):
        """
            参数：
                b_include_details:      <boolean> 是否将详细处理信息也添加到输出的"details"和"details_ls"字段中
                                            其中 "details" 用于记录当前最近一次处理的信息，"details_ls" 用于记录所有历史处理信息
                                            默认为 True
                seed:                   <int> 随机种子
                rng:                    <Random Generator> 给定的随机采样器
                                以上参数二选一
                replay_times:           <int/None> 重播多少次最近一次的处理（重播的意思是保持 self.cal() 中 kwargs 不变）
                                            具体参考 self.replay_last_process() 的介绍
                **kwargs                <> 其他想要传递到 self.cal() 中的参数
        """
        self.b_include_details = b_include_details
        self.rng = None
        self.set_rng(seed=seed, rng=rng)
        self.__replay_times = None
        self.replay_last_process(replay_times=replay_times)

        self.paras = kwargs
        self.random_item_s = self.find_random_item_in_paras(paras=self.paras)

        self.__last_paras = None

    def set_rng(self, seed=None, rng=None):
        """
            设定/重新设定随机采样器

            参数：
                seed:                   <int> 随机种子
                rng:                    <Random Generator> 给定的随机采样器
                                以上参数二选一
        """
        self.rng = get_rng(seed=seed, rng=rng)

    def __call__(self, input_s: dict) -> dict:
        """
            使用时调用该函数
        """
        # 生成处理相关的参数
        if self.__replay_times == 0 or self.__last_paras is None:
            paras = self.determine_paras(paras=self.paras, random_item_s=self.random_item_s)
            self.__last_paras = paras
        else:
            paras = self.__last_paras
            self.__replay_times = self.__replay_times if self.__replay_times < 0 else self.__replay_times - 1

        # 清除上次记录的处理信息
        if "details" in input_s:
            input_s.pop("details")
        #
        res = self.cal(input_s, **paras)
        # 记录处理信息
        if self.b_include_details:
            res["details_ls"] = res.get("details_ls", [])
            temp = dict(
                name=getattr(self, "name", None),
                paras=paras
            )
            temp.update(res.get("details", dict()))
            res["details"] = temp
            res["details_ls"].append(temp)
        elif "details" in input_s:
            input_s.pop("details")

        return res

    @abstractmethod
    def cal(self, input_s: dict, **kwargs) -> dict:
        """
            处理的主要实现
                对输入的 input_s <dict> 进行处理，返回一个 dict
        """
        pass

    @staticmethod
    def find_random_item_in_paras(paras):
        """
             找出 paras 中需要随机采样的项目
        """
        random_item_s = dict()  # {<name_to_item>: <dict of paras to sample_method>, ...}

        def func(idx, value):
            nonlocal random_item_s
            random_item_s[idx] = value
            return value

        ndl.traverse(
            var=paras, match_cond=lambda _, __, value: isinstance(value, (dict,)) and "p_type" in value,
            action_mode="replace", converter=func, b_use_name_as_idx=True, b_traverse_matched_element=False
        )
        return random_item_s

    def determine_paras(self, paras, random_item_s=None):
        """
             对 paras 需要随机采样的项目进行采样，替换，并返回
        """
        if random_item_s is None:
            random_item_s = self.find_random_item_in_paras(paras=paras)

        if len(random_item_s) > 0:
            paras = ndl.copy_(var=paras, b_deepcopy=False)
            for name, values in random_item_s.items():
                ndl.set_value(var=paras, name=name, value=sample_from_feasible_domain(**values, rng=self.rng),
                              b_force=False)
        return paras

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
        self.__replay_times = replay_times
