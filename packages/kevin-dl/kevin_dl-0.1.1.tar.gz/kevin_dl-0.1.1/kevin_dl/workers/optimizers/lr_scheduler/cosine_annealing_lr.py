import math
from kevin_dl.workers.optimizers.lr_scheduler import Base_LR_Scheduler


def cosine_annealing_lr(t, T_max, eta_max, eta_min=0.0):
    """
    根据余弦退火公式计算给定时间步的学习率。

    参数：
    ----------
    t : int or float
        当前时间步（epoch 或 iteration）
    T_max : int or float
        一个完整退火周期的长度
    eta_max : float
        初始最大学习率
    eta_min : float, optional
        最小学习率，默认为 0.0

    返回：
    ----------
    lr : float
        当前时间步对应的学习率
    """
    if t > T_max:
        t = T_max  # 防止超出退火周期

    lr = eta_min + 0.5 * (eta_max - eta_min) * (1 + math.cos(math.pi * t / T_max))
    return lr


class Cosine_Annealing_LR(Base_LR_Scheduler):

    def cal(self, para_value, trigger_value):
        if "eta_max" not in self.paras:
            self.paras["eta_max"] = self.first_call_s["para_value"]
        for k in ["T_max", "eta_max"]:
            assert k in self.paras
        return cosine_annealing_lr(t=trigger_value, **self.paras)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    T_max = 100  # 退火周期长度
    eta_max = 0.1
    eta_min = 0.001

    lrs = [cosine_annealing_lr(t, T_max, eta_max, eta_min) for t in range(T_max + 100)]

    plt.plot(lrs)
    plt.title("Cosine Annealing LR Schedule")
    plt.xlabel("Epoch")
    plt.ylabel("Learning Rate")
    plt.grid(True)
    plt.show()
