import torch
import torch.nn as nn
from kevin_dl.workers.variable import MODELS


def sinusoid_position_embedding(emb_dims, emb_nums):
    """
        生成基于余弦的位置编码
            position_embeddings:
              - 形状： [emb_nums, emb_dims]
              - 计算方式： pe[i, j] = sin(i/10000^(j/emb_dims)) if j%2==0 else cos(i/10000^((j-1)/emb_dims))
            一些技巧：
              - 可以将 10000^(j/emb_dims) 部分抽出来，进行复用
    """
    temp = torch.arange(0, emb_dims, step=2, dtype=torch.float64) / emb_dims
    temp = torch.pow(torch.ones_like(temp) * 10000, exponent=temp)
    temp = temp.unsqueeze(1).repeat(1, 2).reshape(1, -1)[:, :emb_dims]
    res = torch.arange(0, emb_nums, dtype=torch.float64).reshape(-1, 1)
    res = res / temp
    res[:, 0::2] = torch.sin(res[:, 0::2])
    res[:, 1::2] = torch.cos(res[:, 1::2])

    return res.to(dtype=torch.float32)


@MODELS.register(name=":transformer:position_embedding:sinusoid")
def build_sinusoid_position_embedding(emb_dims, emb_nums, b_freeze=False):
    return nn.Embedding.from_pretrained(
        sinusoid_position_embedding(emb_dims=emb_dims, emb_nums=emb_nums), freeze=b_freeze)


class Sinusoid_Position_Embedding(nn.Module):
    def __init__(self, emb_dims, emb_nums, b_freeze=True, **kwargs):
        super().__init__()

        self.pos_emb = nn.Parameter(sinusoid_position_embedding(emb_dims, emb_nums), requires_grad=not b_freeze)

    def forward(self, x):
        return x + self.pos_emb


if __name__ == '__main__':
    emb_dims_ = 150
    emb_nums_ = 15
    position_encoder = Sinusoid_Position_Embedding(emb_dims=emb_dims_, emb_nums=emb_nums_)

    pos_emb = position_encoder(torch.zeros(1, emb_nums_, emb_dims_))
    print(pos_emb.shape)

    # 可视化
    import matplotlib.pyplot as plt

    plt.figure()
    plt.pcolormesh(pos_emb[0], cmap="RdBu")
    plt.xlabel("emb_dims")
    plt.ylabel("emb_nums")
    plt.colorbar()
    plt.show()
