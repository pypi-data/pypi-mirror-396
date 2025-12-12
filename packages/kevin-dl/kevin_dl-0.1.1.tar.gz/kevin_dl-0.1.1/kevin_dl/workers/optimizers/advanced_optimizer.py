import torch
from kevin_toolbox.computer_science.algorithm import for_dict, scheduler
from kevin_dl.workers.optimizers import get_param_groups_from_settings, lr_scheduler


class Advanced_Optimizer:
    def __init__(self, **kwargs):
        """
            为已有优化器增加策略更新等功能

            参数：
                builder:                <Object/func> 优化器类或者创建优化器实例的方法
                settings:               <dict> 优化器的设置
                        其下包括两个键值对：
                        "for_all":          <dict of paras> 优化器的基础设置
                                                若非下面的 for_groups 中专门指定的参数，都将使用该设置进行优化。
                        "for_groups":       <dict> 为指定参数进行另外的设置
                                                形式为：
                                                    {<regular expression>: <dict of paras>, ...}
                                                工作流程：
                                                    首先将参数名满足 <regular expression> 正则表达式的模型参数分为一组，然后根据 <dict of paras> 为
                                                    这组参数设置优化器，<dict of paras> 中缺少的设置将结合前面的 for_all 基础设置进行补全。
                named_parameters:       <list/generator of tuples> 模型参数
                                            形式为 [("para_name", para), ...]，具体可以参考 torch.model.named_parameters()
                strategy:               <dict / list of dict> 待添加的多个策略
                                            将会用于构建 self.strategy_manager <scheduler.Strategy_Manager> 策略管理器。
                                            在调用 self.update_by_state() 时，将会查询 self.strategy_manager 中对于 settings 的更新策略，
                                            并根据更新后的 settings 更新优化器中的 self.param_groups。
        """
        # 默认参数
        paras = {
            #
            "builder": torch.optim.SGD,
            "named_parameters": None,
            #
            "settings": {"for_all": dict(), "for_groups": dict()},
            #
            "strategy": None,
        }

        # 获取参数
        paras = for_dict.deep_update(stem=paras, patch=kwargs)

        # 校验参数
        assert paras["named_parameters"] is not None
        paras["named_parameters"] = list(paras["named_parameters"])
        assert type(paras["builder"]) == type or callable(paras["builder"])

        # 替换 strategy 中 lr_scheduler 部分
        for k, v_s in paras["strategy"].items():
            if k in ["__dict_form", "__trigger_name"]:
                continue
            for key in v_s.keys():
                v = v_s[key]
                if isinstance(v, dict) and v.get("name", "").split(":")[1] == "lr_scheduler":
                    func = getattr(lr_scheduler, v["name"].split(":")[-1])
                    func = func(**{kk: vv for kk, vv in v.items() if kk != "name"})
                    v_s[key] = func

        self.strategy_manager = scheduler.Strategy_Manager(
            override=False, strategy=paras["strategy"]) if paras["strategy"] is not None else None
        self.paras = paras
        self.worker = None
        self._build_worker()

    def _build_worker(self):
        param_groups = get_param_groups_from_settings(named_parameters=self.paras["named_parameters"],
                                                      settings=self.paras["settings"])
        if self.worker is None:
            self.worker = self.paras["builder"](params=param_groups)
        else:
            self.worker.param_groups = []
            for i in param_groups:
                self.worker.add_param_group(i)

    def update_by_state(self, trigger_state, **kwargs):
        """
            调整超参数
        """
        self.paras, action_s_all = self.strategy_manager.cal(trigger_state=trigger_state, var=self.paras)
        if sum(len(i) for i in action_s_all.values()) > 0:
            # 只有有更新的时候才重新设置 worker
            self._build_worker()

    # ------------------------------------ magic func ------------------------------------ #

    # self.key = value
    def __setattr__(self, key, value):
        """
            初始化完成后，对该类实例以 self.key = value 方式进行赋值时，将转为调用 self.worker.key = value。
                方便直接对优化器 self.worker 进行操作。
        """
        if "worker" not in self.__dict__ or key in self.__dict__:
            # worker 未被设置，未完成初始化。或者完成了初始化之后，访问本类中已建立的属性。
            super().__setattr__(key, value)
        else:
            setattr(self.worker, key, value)

    # self.key
    def __getattr__(self, key):
        """
            初始化完成后，对该类实例以 self.key 方式进行访问时，将转为调用 self.worker.key。
                方便直接对优化器 self.worker 进行操作。
        """
        if "worker" not in self.__dict__ or key in self.__dict__:
            # worker 未被设置，未完成初始化。或者完成了初始化之后，访问本类中已建立的属性。
            return super().__getattr__(key)
        else:
            return getattr(self.worker, key)

    def __str__(self):
        return str(self.worker)


if __name__ == '__main__':
    import torch
    from kevin_dl.workers.algorithms.variational_conv.test.example_model import Net

    net = Net(in_channels=3, out_channels=12, n_output=10, mode="variational")

    opt = Advanced_Optimizer(builder=torch.optim.Adam, named_parameters=net.named_parameters())
    print(opt.zero_grad)
    opt.param_groups = []
    print(opt.param_groups)
