import numpy as np
from kevin_toolbox.patches.for_numpy.random import get_rng, truncated_normal


def sample_from_feasible_domain(p_type, p_prob="uniform", **kwargs):
    """
        根据参数设定的可行域和采样方法，采样出结果

        可行域相关参数：
            p_type:             <str> 定义域类型
                                    目前支持：
                                        - "float"
                                        - "int"
                                        - "categorical"
                                    根据不同的定义域类型，需要给出对应的参数。比如：
                                        - p_type="categorical" 时，应该包含可选值列表 choices 参数
                                        - p_type="float"或者"int" 时，应该包含最大、最小、（间隔值）参数 high、low、（step）
            choices:            <list/tuple> 可选值列表
            high:               <int/float>
            low:                <int/float>
                    注意：对于 high 和 low 确定的定义域，边界范围为 [low, high)
            step:               <int/float> 步长

        采样方法相关参数：
            p_prob:             <str/list of float> 采样方法
                                    目前支持：
                                        - "uniform"         均匀分布。
                                        - "normal"          高斯分布。仅支持 p_type="float"或者"int"类型 且设置没有 step 参数的定义域。
                                                                配合参数 high、low 可以实现截断的正态分布。
                                                                当 high、low 设置为 None 时表示不截断。
                                        - <list of float>   离散概率。仅支持离散定义域，
                                                                比如 p_type="float"或者"int" 且设置有 step 参数，以及
                                                                p_type="categorical"。
                                                                要求 离散概率 的数量与 可行值 的数量一致。
                                    根据不同的类型，需要给出对应的参数。比如：
                                        - p_prob="normal" 时，应该包含均值 mean 和标准差 sigma 参数
        其他参数：
            seed:               <int> 随机种子
            rng:                <Random Generator> 给定的随机采样器
                    以上参数二选一
    """
    rng = get_rng(**kwargs)

    if p_type in ("int", "float"):

        if p_prob == "uniform":
            low, high = kwargs.get("low", 0), kwargs.get("high", 1)
            assert high > low
            if "step" not in kwargs:
                v = rng.random() * (high - low) + low
            else:
                v = rng.choice(np.arange(low, high, kwargs["step"]), replace=False)

        elif p_prob == "normal":
            v = truncated_normal(mean=kwargs.get("mean", 0), sigma=kwargs.get("sigma", 1),
                                 low=kwargs.get("low", None), high=kwargs.get("high", None), size=None, rng=rng)

        elif getattr(p_prob, "__len__", lambda: None)() is not None:
            v_ls = np.arange(kwargs.get("low", 0), kwargs.get("high", 1), kwargs["step"])
            assert len(v_ls) == len(p_prob)
            v = rng.choice(v_ls, replace=False, p=p_prob)

        else:
            raise NotImplementedError(f'p_prob {p_prob} not supported!')
        if p_type == "int":
            v = int(v)

    elif p_type == "categorical":
        assert "choices" in kwargs

        if p_prob == "uniform":
            p_prob = np.ones(len(kwargs["choices"]))
        elif p_prob == "normal":
            raise NotImplementedError(f'p_prob {p_prob} not supported for p_type=categorical!')
        elif getattr(p_prob, "__len__", lambda: None)() is not None:
            assert len(p_prob) == len(kwargs["choices"])
        else:
            raise NotImplementedError(f'p_prob {p_prob} not supported!')

        p_prob = np.array(p_prob) / np.sum(p_prob)
        v = rng.choice(kwargs["choices"], replace=False, p=p_prob)
    else:
        raise ValueError

    return v


if __name__ == '__main__':
    inputs = [
        {
            "p_type": "float",
            "p_prob": "normal",
            "high": 10,
            "low": 0,
        },
        {
            "p_type": "float",
            "p_prob": "uniform",
            "high": 1,
            "low": -1,
        },
        {
            "p_type": "int",
            "p_prob": "uniform",
            "high": 180,
            "low": 0,
        },
        {
            "p_type": "categorical",
            "choices": [1, 2, 4, 8, 16]
        }
    ]

    for i in inputs:
        print(sample_from_feasible_domain(**i))
