import torch
import torch.nn as nn
from kevin_dl.workers.models.transformer.blocks import Basic_Encoder_Block
from kevin_dl.workers.variable import MODELS


@MODELS.register(name=":transformer:Encoder")
class Encoder(nn.Module):
    """
        编码器

        工作流程：
            接受 LongTensor 类型的 token_idx_ls 输入，
            使用内部的 word embedding 进行编码，并与 position embedding 相加，
            最后经过 encoder blocks 逐个推理得到输出
    """

    def __init__(self, **kwargs):
        super().__init__()
        paras = {
            # word embedding
            "vocab": None,
            "vocab_size": None,  # vocab 和 vocab_size 二选一，同时为 None 时，表示不使用 word embedding 层
            # position embedding
            "position_embedding": ":transformer:position_embedding:sinusoid",
            # 注意力层
            "emb_dims": None,
            "emb_nums": None,  # 主要用于设置 position embedding 的大小
            "attn_dims": None,
            "head_nums": 8,
            # 前馈层
            "expansion_ratio_in_forward": 4,
            # 多少个 block
            "block_nums": 6,  # int or dict
            # 其他
            "dropout_ratio": 0,
            # 监控
            "b_statistics": False
        }
        paras.update(kwargs)
        paras["vocab_size"] = len(paras["vocab"]) if paras["vocab"] is not None else paras["vocab_size"]

        # word embedding
        self.word_emb_layer = None
        if paras["vocab_size"] is not None:
            self.word_emb_layer = nn.Embedding(paras["vocab_size"], paras["emb_dims"])
        # position embedding
        self.pos_emb_layer = None
        p_emb_builder = MODELS.get(name=paras["position_embedding"], default=None) if paras[
            "position_embedding"] else None
        if p_emb_builder is not None:
            self.pos_emb_layer = p_emb_builder(emb_dims=paras["emb_dims"], emb_nums=paras["emb_nums"], b_freeze=False)
        # dropout
        self.dropout = nn.Dropout(paras["dropout_ratio"])

        # encoder blocks
        self.block_ls = nn.ModuleList([
            Basic_Encoder_Block(emb_dims=paras["emb_dims"], attn_dims=paras["attn_dims"], head_nums=paras["head_nums"],
                                expansion_ratio_in_forward=paras["expansion_ratio_in_forward"],
                                dropout_ratio=paras["dropout_ratio"], b_statistics=paras["b_statistics"]) for _ in
            range(paras["block_nums"])
        ])

        self.paras = paras

    def forward(self, x, mask=None):
        """
            参数：
                x:              [bz, emb_nums]
        """
        # embedding
        if self.word_emb_layer is not None:
            x = self.word_emb_layer(x)
        x = self.dropout(x)
        if self.pos_emb_layer is not None:
            x = x + self.pos_emb_layer(torch.arange(x.shape[1], device=x.device))
        # encoder blocks
        for block in self.block_ls:
            x = block(x, mask=mask)

        return x


if __name__ == '__main__':
    batch_size = 3
    emb_dims_ = 15
    emb_nums_ = 5
    enc = Encoder(emb_dims=emb_dims_, emb_nums=emb_nums_, attn_dims=10, head_nums=3, vocab_size=20, b_statistics=True)
    x_ = torch.randint(low=0, high=20, size=(batch_size, emb_nums_))
    mask_ = torch.triu(torch.ones(5, 5), diagonal=1)

    y_ = enc(x_, mask_)
    print(y_.shape)
    print(y_)
