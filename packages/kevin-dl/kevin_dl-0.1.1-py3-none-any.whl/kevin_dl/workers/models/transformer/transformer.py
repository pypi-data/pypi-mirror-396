import torch
import torch.nn as nn
from kevin_dl.workers.models.transformer import Decoder, Encoder
from kevin_dl.workers.models.transformer.attention import generate_attention_mask


class Transformer(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        paras = {
            #
            "vocab": None,  # 词典
            # 注意力层
            "emb_dims": None,  # int or dict like {"enc": <int>, "dec": <int>}
            "emb_nums": None,  # int or dict
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
        # 检查参数
        for k, v in paras.items():
            if not isinstance(v, (dict,)):
                paras[k] = {i: v for i in ["enc", "dec"]}

        # encoder
        self.encoder = Encoder(**{k: v["enc"] for k, v in paras.items()},
                               vocab_size=len(paras["vocab"]["enc"]))
        # decoder
        self.decoder = Decoder(**{k: v["dec"] for k, v in paras.items()},
                               vocab_size=len(paras["vocab"]["dec"]))

        # projection
        self.projection = nn.Linear(paras["emb_dims"]["dec"], len(paras["vocab"]["dec"]), bias=False)

        self.paras = paras

    def generate_mask(self, enc_inputs=None, dec_inputs=None, tokens_to_mask=None, mode="mask_enc"):
        if mode == "mask_enc":
            assert enc_inputs is not None
            mask = generate_attention_mask(
                q_nums=enc_inputs.shape[1], kv_tokens=enc_inputs,
                tokens_to_mask=self.paras["vocab"]["enc"].lookup_indices(
                    ["<pad>", ]) if tokens_to_mask is None else tokens_to_mask,
                b_mask_subsequent=False
            )
        elif mode == "mask_dec":
            assert dec_inputs is not None
            mask = generate_attention_mask(
                q_nums=dec_inputs.shape[1], kv_tokens=dec_inputs,
                tokens_to_mask=self.paras["vocab"]["dec"].lookup_indices(
                    ["<pad>", ]) if tokens_to_mask is None else tokens_to_mask,
                b_mask_subsequent=True
            )
        elif mode == "mask_enc_to_dec":
            assert enc_inputs is not None and dec_inputs is not None
            mask = generate_attention_mask(
                q_nums=dec_inputs.shape[1], kv_tokens=enc_inputs,
                tokens_to_mask=self.paras["vocab"]["enc"].lookup_indices(
                    ["<pad>", ]) if tokens_to_mask is None else tokens_to_mask,
                b_mask_subsequent=False
            )
        else:
            raise NotImplementedError(f'mode={mode} is not supported.')
        return mask

    def forward(self, enc_inputs, dec_inputs,
                mask_enc=None, mask_enc_to_dec=None, mask_dec=None):
        """
            按照 teacher forcing 的方式进行推理
                一般在训练时使用

            之所以要支持将 mask_enc 放到外面去生成，是因为转换为 onnx 时，生成 mask 的过程中会引入 where 节点
                该节点目前（1.17.3）并不被 onnxruntime 支持，因此通过将 mask 放到外面去生成，可以避免生成 onnx 带有 where 节点，从而能被
                当前的 onnxruntime 支持。具体可以看本脚本中 if __name__ == '__main__' 部分。
        """
        # encode
        mask_enc = self.generate_mask(enc_inputs=enc_inputs, mode="mask_enc") if mask_enc is None else mask_enc
        enc_outs = self.encoder(enc_inputs, mask=mask_enc)

        # decode
        mask_enc_to_dec = self.generate_mask(enc_inputs=enc_inputs, dec_inputs=dec_inputs,
                                             mode="mask_enc_to_dec") if mask_enc_to_dec is None else mask_enc_to_dec
        mask_dec = self.generate_mask(dec_inputs=dec_inputs, mode="mask_dec") if mask_dec is None else mask_dec
        dec_outs = self.decoder(dec_inputs, enc_outs=enc_outs, mask_dec=mask_dec, mask_enc=mask_enc_to_dec)
        pred = self.projection(dec_outs)
        return pred

    @torch.no_grad()
    def inference(self, enc_inputs):
        """
            按照 seq2seq 的方式推理
                一般用于测试和实际使用时

            参数：
                enc_inputs:             [1, emb_nums]
        """
        assert enc_inputs.shape[0] == 1

        # encode
        # 按照最大输入长度进行裁剪
        enc_inputs = enc_inputs[:, :self.encoder.paras["emb_nums"]]
        # 去除末尾的 "<pad>"
        temp = torch.nonzero(
            enc_inputs.contiguous().view(-1) == self.paras["vocab"]["enc"]["<pad>"])
        if len(temp) > 0:
            enc_inputs = enc_inputs[:, :min(temp)[0]]
        # 由于在 enc_inputs 和 后面生成的 dec_inputs 中都没有 <pad>，所以不需要 mask
        enc_outs = self.encoder(enc_inputs, mask=None)

        # decode
        dec_inputs = torch.tensor(self.paras["vocab"]["dec"]["<sos>"], device=enc_inputs.device).reshape(1, -1)
        # 依次迭代直至遇到生成 <eos> 或者到达最大预测上限
        for _ in range(self.decoder.paras["emb_nums"]):
            dec_outs = self.decoder(dec_inputs, enc_outs=enc_outs, mask_dec=None, mask_enc=None)
            pred = self.projection(dec_outs)
            # 取最后一个 token
            pred_ids = pred[:, -1:, :].argmax(dim=-1)
            #
            if pred_ids == self.paras["vocab"]["dec"]["<eos>"]:
                break
            dec_inputs = torch.cat([dec_inputs, pred_ids], dim=-1)
        return dec_inputs


if __name__ == '__main__':
    from kevin_dl.reimplement.transformer.dataset import Translate_Eng_Fra

    dataset = Translate_Eng_Fra(token_nums=10)
    vocab = dataset.vocab_s["eng"]

    batch_size = 7
    emb_dims_ = 15
    dec_emb_nums_ = 5
    enc_emb_nums_ = 6
    net = Transformer(emb_dims=emb_dims_, emb_nums=dict(enc=enc_emb_nums_, dec=dec_emb_nums_),
                      attn_dims=7, head_nums=3, vocab=vocab, dropout_ratio=0.1, block_nums=3, b_statistics=True)

    enc_inputs = torch.randint(low=0, high=20, size=(batch_size, enc_emb_nums_))
    dec_inputs = torch.randint(low=0, high=20, size=(batch_size, dec_emb_nums_))
    y_ = net(enc_inputs=enc_inputs, dec_inputs=dec_inputs)
    print(y_.shape)
    print(y_)

    # breakpoint()
    print(net)

    # 获取某一个 mha 层的 scores
    for k, v in list(net.named_modules()):
        if not k.endswith(("mha_0", "mha_1")):
            continue
        print(k, v)
        print(v.statistics.keys())
        print(v.statistics['scores'].shape)

    # 推理
    res = net.inference(enc_inputs=torch.tensor(
        [vocab.lookup_indices(["<sos>", "I", "am", "a", "student", ".", ".", "<eos>", "<pad>", "<pad>", ])]
    ))
    print(res)
    print(vocab.lookup_tokens(res[0].tolist()))

    # 保存成 onnx 来看模型结构。
    import os
    from kevin_dl.deploy import convert_torch_to_onnx

    #
    convert_torch_to_onnx(
        model=net,
        inputs=(
            enc_inputs, dec_inputs,
            net.generate_mask(enc_inputs=enc_inputs, mode="mask_enc"),
            net.generate_mask(enc_inputs=enc_inputs, dec_inputs=dec_inputs, mode="mask_enc_to_dec"),
            net.generate_mask(dec_inputs=dec_inputs, mode="mask_dec")
        ),
        output_dir=os.path.join(os.path.dirname(__file__), "temp")
    )
