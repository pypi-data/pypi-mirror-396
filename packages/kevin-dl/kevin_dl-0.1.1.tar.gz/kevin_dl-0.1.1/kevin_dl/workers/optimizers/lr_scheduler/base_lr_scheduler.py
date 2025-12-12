import copy
from abc import ABC, abstractmethod


class Base_LR_Scheduler(ABC):
    """
        基础学习率调度器
    """

    def __init__(self, **kwargs):
        self.paras = kwargs
        self.first_call_s = None
        self.t_offset = kwargs.pop("t_offset", None)

    def __call__(self, para_value, trigger_value):
        if self.first_call_s is None:
            self.first_call_s = dict(
                para_value=para_value,
                trigger_value=trigger_value
            )
        if self.t_offset is None:
            self.t_offset = self.first_call_s["trigger_value"]
        return self.cal(para_value, trigger_value - self.t_offset)

    @abstractmethod
    def cal(self, para_value, trigger_value):
        return
