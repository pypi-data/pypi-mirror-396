import math
from kevin_dl.workers.optimizers.lr_scheduler import Base_LR_Scheduler


def cosine_annealing_warm_restarts_lr(t, T_0, eta_max, eta_min=0.0, T_mult=1):
    """
    计算给定时间步下的 Cosine Annealing Warm Restarts 学习率。

    参数
    ----------
    t : int or float
        当前的训练步数（epoch 或 iteration）
    T_0 : int
        第一个周期的长度
    T_mult : float
        每次重启后周期长度的倍率增长系数（例如 2 表示每次周期翻倍）
    eta_max : float
        最大学习率
    eta_min : float, optional
        最小学习率，默认为 0.0

    返回
    ----------
    lr : float
        当前步的学习率
    """

    # 1️⃣找出当前属于第几个周期，以及当前周期内的步数
    T_i = T_0  # 当前周期长度
    T_sum = 0  # 已经过的总步数

    while t >= T_sum + T_i:
        T_sum += T_i
        T_i *= T_mult  # 周期增长

    # 当前周期内的步数（从0开始）
    t_i = t - T_sum

    # 2️⃣按余弦公式计算该周期内的学习率
    lr = eta_min + 0.5 * (eta_max - eta_min) * (1 + math.cos(math.pi * t_i / T_i))

    return lr


class Cosine_Annealing_Warm_Restarts_LR_Scheduler(Base_LR_Scheduler):

    def cal(self, para_value, trigger_value):
        if "eta_max" not in self.paras:
            self.paras["eta_max"] = self.first_call_s["para_value"]
        for k in ["T_0", "eta_max"]:
            assert k in self.paras
        return cosine_annealing_warm_restarts_lr(t=trigger_value, **self.paras)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    T_0 = 10  # 初始周期长度
    T_mult = 2  # 每次周期翻倍
    eta_max = 0.1
    eta_min = 0.001

    # 计算 100 个 epoch 下的学习率
    lrs = [cosine_annealing_warm_restarts_lr(t, T_0, T_mult, eta_max, eta_min) for t in range(100)]

    plt.plot(lrs)
    plt.title("Cosine Annealing Warm Restarts (T_0=10, T_mult=2)")
    plt.xlabel("Epoch")
    plt.ylabel("Learning Rate")
    plt.grid(True)
    plt.show()
