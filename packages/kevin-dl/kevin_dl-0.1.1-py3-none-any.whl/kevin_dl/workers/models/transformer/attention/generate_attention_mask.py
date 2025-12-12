import torch


def generate_attention_mask(q_nums: int, kv_tokens: torch.Tensor, tokens_to_mask=None,
                            b_mask_subsequent=False) -> torch.Tensor:
    """
        生成注意力机制中，对 scores 的掩码。

        什么是掩码？作用是？
            该掩码 mask 是一个与 scores 具有相同形状的0、1矩阵，其中标记为 1 部分意味着对应位置的 scores 将会填充为负无穷，
            意味着在经过其后的 softmax 处理后，该部分的值将为 0。

        使用场景：
            在 transformer 的训练过程中，
            - 对于 encoder，对其输入句子中 <pad> 标记进行遮盖。
                比如输入为 [<sos>, "你", "好", <eos>, <pad>, <pad>]
                那么就应该生成一个最后两列都为 0 的 mask 用于消除 <pad> 的影响。
            - 对于 decoder，除了需要注意 <pad> 标记，还需要保证前一个 token 不能看到后一个 token 的信息，亦即对于 n 个 token，其 scores 中
                后面 n-1 个元素应该置为负无穷。仅考虑后者，此时 mask 应该是一个对角线为 0，上三角为 1 的矩阵。
                继续以上面的例子，此时的 mask 矩阵应该是：
                    [[0,1,1,1,1],
                     [0,0,1,1,1],
                     [0,0,0,1,1],
                     [0,0,0,1,1],
                     [0,0,0,1,1]]

        参数：
            q_nums:                 <int>
            kv_tokens:              [(bz), kv_nums] 对应于 K、V 位置的 tokens
            tokens_to_mask:         <list/tuple/set of token> 需要哪些种类的 token
            b_mask_subsequent:      <boolean> 是否需要让前一个 token 不能看到后一个 token 的信息

        返回:
            mask:               [(bz), q_nums, kv_nums] dtype=boolean
    """
    # 对指定 tokens 进行遮挡
    mask = torch.zeros_like(kv_tokens, dtype=torch.bool)
    for token in tokens_to_mask:
        mask.masked_fill_(kv_tokens.data.eq(token), 1)

    # mask: [(bz), q_nums, kv_nums]
    mask = mask.unsqueeze(-2).repeat(*[1] * (mask.ndim - 1), q_nums, 1)

    # 对上三角进行遮挡
    if b_mask_subsequent:
        mask.masked_fill_(
            torch.triu(torch.ones(q_nums, mask.shape[-1]), diagonal=1).data.eq(1).to(device=mask.device), 1)

    return mask


if __name__ == '__main__':
    kv_tokens_ = torch.tensor([[1, 2, 4, 4, 5],
                               [1, 2, 3, 4, 5]])
    mask_ = generate_attention_mask(q_nums=10, kv_tokens=kv_tokens_, tokens_to_mask=[3, 5], b_mask_subsequent=True)
    print(mask_.shape)
    print(mask_)

    kv_tokens_ = torch.tensor([1, 2, 3, 4, 5])
    mask_ = generate_attention_mask(q_nums=10, kv_tokens=kv_tokens_, tokens_to_mask=[3, 5], b_mask_subsequent=True)
    print(mask_.shape)
    print(mask_)
