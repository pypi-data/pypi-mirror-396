from kevin_dl.workers.optimizers.lr_scheduler import Base_LR_Scheduler


def linear_lr(t, T_max, base_lr, start_factor=0.1, end_factor=1.0):
    """
    根据线性公式计算给定时间步的学习率。

    参数：
    ----------
    t : int or float
        当前时间步（epoch）
    T_max : int or float
        线性变化持续的总步数
    base_lr:            <float>
    start_factor:       <float>
        起始学习率
    end_factor:         <float>
        结束学习率

    返回：
    ----------
    lr : float
        当前时间步的学习率
    """
    start_factor, end_factor = base_lr * start_factor, base_lr * end_factor
    # 防止超出边界
    t = min(t, T_max)
    lr = start_factor + (end_factor - start_factor) * (t / T_max)
    return lr


class Linear_LR(Base_LR_Scheduler):

    def cal(self, para_value, trigger_value):
        if "base_lr" not in self.paras:
            self.paras["base_lr"] = self.first_call_s["para_value"]
        for k in ["T_max", "base_lr"]:
            assert k in self.paras
        return linear_lr(t=trigger_value, **self.paras)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    eta_start = 0.05
    eta_end = 1.0
    T_max = 40

    lrs = [linear_lr(t, T_max, base_lr=0.05, start_factor=eta_start, end_factor=eta_end) for t in range(100)]

    plt.plot(lrs)
    plt.title("Linear LR Schedule")
    plt.xlabel("Epoch")
    plt.ylabel("Learning Rate")
    plt.grid(True)
    plt.show()
