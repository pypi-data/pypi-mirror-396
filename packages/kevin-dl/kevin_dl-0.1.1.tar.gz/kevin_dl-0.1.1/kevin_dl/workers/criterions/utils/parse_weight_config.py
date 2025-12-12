import numpy as np
from kevin_toolbox.patches.for_numpy.linalg import softmax


def parse_weight_config(cfg_ls, weights_len, b_normalize=False, temperature=1.0):
    """
        解释权重配置

        参数：
            cfg_ls:         <list of dict>
                            每个元素表示权重的计算过程，应该包含以下键值对：
                                "range":    <tuple of two int/tuple> 要指定的权重的位置
                                                包头不包尾
                                                比如 (2, None) 就表示这部分计算的是 第3个 到 最后 的权重
                                计算方式:
                                "func":     <str start with eval or callable> 函数
                                                形如 def xxx(idx_ls):   其中输入的是权重的位置列表 idx_ls=list(range(...))
                                "lookup_table": <list> 查找表
            weights_len:    <int> 权重的长度
            b_normalize:    <boolean> 是否将权重归一化
            temperature:    <float> 温度系数
                            它越大，输出的概率分布越平缓。
                            仅在归一化开启时起效
    """
    weights = np.zeros(weights_len)
    for cfg in cfg_ls:
        assert "range" in cfg
        w_ls = weights[cfg["range"][0]:cfg["range"][1]]
        #
        if "func" in cfg:
            func = eval(cfg["func"][6:]) if cfg["func"].startswith("<eval>") else cfg["func"]
            v_ls = func(np.arange(len(w_ls)) + (0 if cfg["range"][0] is None else cfg["range"][0]))
        elif "lookup_table" in cfg:
            v_ls = cfg["lookup_table"]
        else:
            raise ValueError("cfg must contain 'func' or 'lookup_table'")
        w_ls[:] = np.asarray(v_ls)[:len(w_ls)]

    if b_normalize:
        weights = softmax(x=weights, temperature=temperature, b_use_log_over_x=True)

    return weights


if __name__ == "__main__":
    from kevin_toolbox.patches.for_matplotlib.common_charts import plot_lines

    data_s = dict()
    for t_ in [-100, -10, -4, -3, -2, 0.8, 1, 2, 3, 4, 10, 100]:
        temp = parse_weight_config(cfg_ls=[
            {
                "range": (0, 14),
                "func": "<eval>lambda idx_ls: np.linspace(0.4,2.2,len(idx_ls)+1)[:-1]",
            },
            {
                "range": (14, 40),
                "func": "<eval>lambda idx_ls: np.linspace(2.2,5,len(idx_ls)+1)[:-1]",
            },
            {
                "range": (40, 100),
                "func": "<eval>lambda idx_ls: np.linspace(5,6.2,len(idx_ls)+1)[:-1]",
            },
            {
                "range": (100, None),
                "func": "<eval>lambda idx_ls: [6.2]*len(idx_ls)",
            },
        ], b_normalize=True, weights_len=100, temperature=t_
        )
        print(sum(temp))
        data_s[f't={t_}'] = temp
    data_s.update({"x": list(range(len(temp)))})
    plot_lines(data_s=data_s, title="mean_variance_loss", x_name="x")
