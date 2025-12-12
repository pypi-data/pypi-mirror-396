import torch
import torch.nn as nn
from kevin_dl.workers.models.transformer.attention import Multi_Head_Attention
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":transformer:blocks:Basic_Encoder_Block")
class Basic_Encoder_Block(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        paras = {
            # 注意力层
            "emb_dims": None,
            "attn_dims": None,
            "head_nums": 8,
            # 前馈层
            "forward_dims": None,  # 默认根据 emb_dims 和 expansion_ratio_in_forward 进行推导
            "expansion_ratio_in_forward": 4,
            # 其他
            "dropout_ratio": 0,
            # 监控
            "b_statistics": False
        }
        paras.update(kwargs)
        # 检查参数
        if paras["forward_dims"] is None:
            paras["forward_dims"] = int(paras["expansion_ratio_in_forward"] * paras["emb_dims"])

        # 注意力层
        self.mha = Multi_Head_Attention(emb_dims=paras["emb_dims"], attn_dims=paras["attn_dims"],
                                        head_nums=paras["head_nums"], b_statistics=paras["b_statistics"])
        self.ln_0 = nn.LayerNorm(paras["emb_dims"])
        # 前馈层
        self.ffn = nn.Sequential(
            nn.Linear(paras["emb_dims"], paras["forward_dims"]),
            nn.ReLU(),
            nn.Linear(paras["forward_dims"], paras["emb_dims"]),
        )
        self.ln_1 = nn.LayerNorm(paras["emb_dims"])
        # dropout
        self.dropout = nn.Dropout(paras["dropout_ratio"])

        self.paras = paras

    def forward(self, x, mask=None):
        """
            参数：
                x:              [bz, emb_nums, emb_dims]
                mask:           [(bz), emb_nums, emb_dims]
        """
        # 注意力层
        x = self.dropout(self.mha(q=x, k=x, v=x, mask=mask)) + x
        x = self.ln_0(x)
        # 前馈层
        x = self.dropout(self.ffn(x)) + x
        x = self.ln_1(x)
        return x


if __name__ == '__main__':
    x_ = torch.randn(2, 10, 32)
    y_ = Basic_Encoder_Block(emb_dims=32, attn_dims=32, head_nums=8)(x_)
    print(y_.shape)
