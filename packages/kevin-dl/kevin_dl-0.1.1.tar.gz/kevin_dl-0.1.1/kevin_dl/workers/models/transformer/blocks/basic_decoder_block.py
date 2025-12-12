import torch
import torch.nn as nn
from kevin_dl.workers.models.transformer.attention import Multi_Head_Attention
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":transformer:blocks:Basic_Decoder_Block")
class Basic_Decoder_Block(nn.Module):
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
            "b_statistics": False,
        }
        paras.update(kwargs)
        # 检查参数
        if paras["forward_dims"] is None:
            paras["forward_dims"] = int(paras["expansion_ratio_in_forward"] * paras["emb_dims"])

        # 注意力层
        self.mha_0 = Multi_Head_Attention(emb_dims=paras["emb_dims"], attn_dims=paras["attn_dims"],
                                          head_nums=paras["head_nums"], b_statistics=paras["b_statistics"])
        self.ln_0 = nn.LayerNorm(paras["emb_dims"])
        # （用于融合encoder的信息）
        self.mha_1 = Multi_Head_Attention(emb_dims=paras["emb_dims"], attn_dims=paras["attn_dims"],
                                          head_nums=paras["head_nums"], b_statistics=paras["b_statistics"])
        self.ln_1 = nn.LayerNorm(paras["emb_dims"])
        # 前馈层
        self.ffn = nn.Sequential(
            nn.Linear(paras["emb_dims"], paras["forward_dims"]),
            nn.ReLU(),
            nn.Linear(paras["forward_dims"], paras["emb_dims"]),
        )
        self.ln_2 = nn.LayerNorm(paras["emb_dims"])
        # dropout
        self.dropout = nn.Dropout(paras["dropout_ratio"])

        self.paras = paras

    def forward(self, x, enc_outs, mask_dec=None, mask_enc=None):
        """
            参数：
                x:              [bz, emb_nums, emb_dims]
                mask_dec:       [(bz), emb_nums, emb_dims]
                mask_enc:       [(bz), emb_nums, enc_emb_dims]  由于在第二个注意力层中使用了 encoder 的输出作为了 K、V，所以也需要知道其 mask
        """
        # 注意力层
        x = self.dropout(self.mha_0(q=x, k=x, v=x, mask=mask_dec)) + x
        x = self.ln_0(x)
        # encoder生成K、V矩阵，decoder生成Q矩阵
        x = self.dropout(self.mha_1(q=x, k=enc_outs, v=enc_outs, mask=mask_enc)) + x
        x = self.ln_1(x)
        # 前馈层
        x = self.dropout(self.ffn(x)) + x
        x = self.ln_1(x)
        return x


if __name__ == '__main__':
    x_ = torch.randn(2, 10, 32)
    enc_outs_ = torch.randn(2, 15, 32)
    y_ = Basic_Decoder_Block(emb_dims=32, attn_dims=32, head_nums=8)(x_, enc_outs_)
    print(y_.shape)
