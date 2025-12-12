import numpy as np
from kevin_toolbox.math.utils import split_integer_most_evenly
from kevin_toolbox.computer_science.algorithm import for_seq
from kevin_toolbox.patches.for_numpy.random import get_rng

rd = np.random.RandomState()


def generate_k_fold_indices(size, n_splits=3, val_split_idx=0, shuffle=True, seed=None, rng=None):
    """
        参数：
            val_split_idx:      <int/list of int> 选取第几个分块作为 val 验证集
                                    当为列表时，表示选取多个分块
    """
    if not hasattr(val_split_idx, "__len__"):
        val_split_idx = [val_split_idx]
    for i in val_split_idx:
        assert 0 <= i < size
    assert len(val_split_idx) == len(set(val_split_idx))

    rng = get_rng(seed=seed, rng=rng)

    indices = np.arange(size)
    if shuffle:
        indices = rng.permutation(indices)
    indices = indices.tolist()

    count = 0
    chunk_ls = []
    for num in split_integer_most_evenly(x=size, group_nums=n_splits):
        chunk_ls.append(indices[count:count + num])
        count += num

    val_indices = for_seq.flatten_list(ls=[chunk_ls[i] for i in val_split_idx])
    train_indices = for_seq.flatten_list(ls=[chunk for i, chunk in enumerate(chunk_ls) if i not in val_split_idx])
    return val_indices, train_indices


if __name__ == '__main__':
    print(generate_k_fold_indices(size=10, val_split_idx=2))
