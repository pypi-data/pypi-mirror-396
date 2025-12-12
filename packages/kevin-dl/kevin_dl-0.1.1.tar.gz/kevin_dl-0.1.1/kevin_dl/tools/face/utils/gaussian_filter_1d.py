import numpy as np
from scipy.stats import norm


def gaussian_filter_1d(x_ls, y_ls, sigma=3, decimals=2, st=None, ed=None, period=None):
    """
        对以 x_ls 为位置，y_ls 为权重的序列，进行高斯平滑

        参数：
            st:                 <float> 输出的范围的起始。
                                不指定时，默认为 min(x_ls)-3*sigma
            ed:                 <float> 输出的范围的结束。
                                不指定时，默认为 max(x_ls)+3*sigma
                                包头不包尾，范围为 [st, ed)
            period:             <float> 周期长度。
                                当指定了period，则 st, ed 的设置无效，此时输出范围为 [0, period)
    """
    assert len(x_ls) == len(y_ls)
    if period is not None:
        st, ed = 0, period
        duplicates = int(np.ceil(3 * sigma / period) + 1)
        x_ls = [i % period for i in x_ls]
    else:
        st = st if st is not None else min(x_ls) - 3 * sigma
        ed = ed if ed is not None else max(x_ls) + 3 * sigma
        duplicates = 1

    X = np.arange(st, ed, 1 / 10 ** decimals)

    Y_base = np.zeros_like(X)
    Y = np.zeros_like(X)
    for x, y in zip(x_ls, y_ls):
        temp = norm.pdf(X, loc=x, scale=sigma)
        for i in range(1, duplicates):
            temp += norm.pdf(X, loc=x + i * period, scale=sigma)
            temp += norm.pdf(X, loc=x - i * period, scale=sigma)
        # 计算 y_ls 值都为 1 时，分别以 x_ls 为中心进行叠加的高斯分布，以此值为基准对后续结果进行 bias fix
        Y_base += temp
        Y += temp * y

    Y /= np.maximum(Y_base, 1e-15)

    return X, Y


if __name__ == '__main__':
    from kevin_toolbox.patches.for_matplotlib.common_charts import plot_lines

    x_ls = np.random.choice(np.arange(-10, 10, 1), 10, replace=False)
    y_ls = np.random.rand(10) * 10
    print(x_ls)
    print(y_ls)

    # data_s = dict()
    # for sigma in [0.1, 0.5, 1, 3, 5, 1000]:
    #     X, Y = gaussian_filter_1d(x_ls=x_ls, y_ls=y_ls, sigma=sigma, decimals=2, st=min(x_ls), ed=max(x_ls))
    #     data_s["X"] = X
    #     data_s[f'Y_sigma_{sigma}'] = Y
    # plot_lines(data_s=data_s, title="Gaussian Filter", x_name="X", output_dir=None)
    # print(np.mean(y_ls))
    # print(X[np.argmax(Y)])

    # 周期
    data_s = dict()
    for sigma in [0.01, 0.05, 0.1, 0.5, 1, 3, 5]:
        X, Y = gaussian_filter_1d(x_ls=x_ls, y_ls=y_ls, sigma=sigma, decimals=2, period=1.1)
        data_s["X"] = X
        data_s[f'Y_sigma_{sigma}'] = Y
    plot_lines(data_s=data_s, title="Gaussian Filter", x_name="X", output_dir=None)
