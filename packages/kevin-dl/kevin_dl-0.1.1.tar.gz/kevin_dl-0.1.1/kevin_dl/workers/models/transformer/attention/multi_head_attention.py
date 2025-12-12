import torch
import torch.nn as nn


class Multi_Head_Attention(nn.Module):
    r"""
        多头注意力机制

        工作流程：
            对于每个注意力头，其运算为：
                输入：
                    Q: [bz, q_nums, q_dims]
                    K: [bz, kv_nums, k_dims]
                    V: [bz, kv_nums, v_dims]
                参数：
                    W_{q,i}:    [q_dims, qk_a_dims]
                    W_{k,i}:    [k_dims, qk_a_dims]
                    W_{v,i}:    [v_dims, v_a_dims]
                输出：
                    A_i = softmax( (Q@W_{q,i}) @ (K@W_{k,i})^{\top} / \sqrt{d_k}, axis=-1) @ (V@W_{v,i})
                    A_i: [bz, q_nums, v_a_dims]
            然后将多个注意力头的结果进行 concat：
                A = concat([A_0, ..., A_i, ...], axis=-1)
                A: [bz, q_nums, head_nums * v_dims]
            最后使用 fc 层调整特征维度大小：
                output = fc(A)
                output: [bz, q_nums, emb_dims]
    """

    def __init__(self, **kwargs):
        """
            参数：
                emb_dims:           <int/dict> 输入的 Q、K、V 矩阵最后一个维度的大小。
                                        应该是形如 {"q": <q_dims>, "k": <k_dims>, "v": <v_dims>} 的矩阵，
                                        当输入为单个 int 时，将解释为最后一个维度具有相同的大小。
                attn_dims:          <int/dict> 参数 W_q、W_k、W_v 矩阵最后一个维度的大小
                                        应该是形如 {"q": <qk_a_dims>, "k": <qk_a_dims>, "v": <v_a_dims>} 的矩阵，
                                            注意 W_q、W_k 最后一个维度的大小要相等
                                        当输入为单个 int 时，将解释为最后一个维度具有相同的大小。
                out_dim:            <int> 输出时最后一个维度的大小。
                                        默认为 None，此时表示与 emb_dims["q"] 相同。
                head_nums:          <int> 注意力头的数量。
                                        默认为 1.
                b_statistics:       <boolean> 是否取出计算过程中产生的中间变量，取出的中间变量将保存在 self.statistics 中
                                        目前支持取出的变量有：
                                            - scores 矩阵
                                            - 经过 W_q,W_k,W_v 处理后的 q_a,k_a,v_a 等
                                                注意 k_a 是经过转置的。
        """
        super().__init__()
        paras = {
            "emb_dims": None,
            "attn_dims": None,
            "out_dim": None,
            "head_nums": 1,
            # 监控
            "b_statistics": False,
        }
        paras.update(kwargs)
        for k in ["emb_dims", "attn_dims"]:
            if not isinstance(paras[k], (dict,)):
                paras[k] = {i: paras[k] for i in ["q", "k", "v"]}
        assert paras["attn_dims"]["q"] == paras["attn_dims"]["k"]
        assert paras["head_nums"] >= 1
        if paras["out_dim"] is None:
            paras["out_dim"] = paras["emb_dims"]["q"]

        # 参数
        for k in ["q", "k", "v"]:
            setattr(self, f'W_{k}', nn.Linear(paras["emb_dims"][k], paras["attn_dims"][k] * paras["head_nums"]))
        self.linear = nn.Linear(paras["head_nums"] * paras["attn_dims"]["v"], paras["out_dim"])

        self.paras = paras
        self._state_s = dict()

    def forward(self, q, k, v, mask=None) -> torch.Tensor:
        """
            参数：
                q:                  [bz, q_nums, qk_dims]
                k:                  [bz, kv_nums, qk_dims]
                v:                  [bz, kv_nums, v_dims]
                mask:               [(bz), q_nums, kv_nums] 用于指定 q、k 所乘得到 scores 矩阵中，哪些部分不参与 softmax 计算
                                        系0、1矩阵，其中元素 1 对应位置不参与 softmax 计算。
        """
        assert k.shape[1] == v.shape[1]
        q_nums, qk_a_dims, kv_nums, v_a_dims = q.shape[1], self.paras["attn_dims"]["q"], \
            k.shape[1], self.paras["attn_dims"]["v"]
        head_nums = self.paras["head_nums"]
        bz = q.shape[0]

        # q_a : [batch_size, head_nums, q_nums, qk_a_dims]
        q_a = self.W_q(q).view(bz, q_nums, head_nums, qk_a_dims).transpose(1, 2)
        # v_a : [batch_size, head_nums, kv_nums, v_a_dims]
        v_a = self.W_v(v).view(bz, kv_nums, head_nums, v_a_dims).transpose(1, 2)
        # k_a : [batch_size, head_nums, qk_a_dims, kv_nums]
        k_a = self.W_k(k).transpose(1, 2).contiguous().view(bz, head_nums, qk_a_dims, kv_nums)

        # scores: [batch_size, head_nums, q_nums, kv_nums]
        scores = q_a @ k_a / torch.sqrt(torch.tensor(qk_a_dims, dtype=float))
        if mask is not None:
            scores.masked_fill_(mask.unsqueeze(-3).to(dtype=torch.bool), -1e9)
        scores = torch.softmax(scores, dim=-1)

        # out: [batch_size, q_nums, head_nums*v_a_dims]
        out_0 = (scores @ v_a).transpose(1, 2).contiguous().view(bz, q_nums, -1)

        # out: [batch_size, q_nums, out_dim]
        out = self.linear(out_0)

        # 记录中间变量
        if self.paras["b_statistics"]:
            temp = locals()
            self._state_s = {k: temp[k].clone().detach() for k in ("scores", "q_a", "k_a", "v_a")}

        return out

    # --------------------------- 辅助功能 --------------------------- #
    def read_statistics(self):
        return self._state_s

    @property
    def statistics(self):
        return self.read_statistics()


if __name__ == '__main__':
    q_nums_, qk_a_dims_, kv_nums_, v_a_dims_ = 5, 15, 7, 10
    q_ = torch.randn(2, q_nums_, 13)
    k_ = torch.randn(2, kv_nums_, 17)
    v_ = torch.randn(2, kv_nums_, 23)
    mask_ = torch.randint(0, 2, (2, q_nums_, kv_nums_))

    mha = Multi_Head_Attention(
        emb_dims={"q": q_.shape[-1], "k": k_.shape[-1], "v": v_.shape[-1]},
        attn_dims={"q": qk_a_dims_, "k": qk_a_dims_, "v": v_a_dims_},
        head_nums=3,
        out_dim=20,
        b_statistics=True
    )
    res = mha(q_, k_, v_, mask=mask_)
    print(res.shape)
    print(mask_)
    print({k: v.shape for k, v in mha.statistics.items()})
