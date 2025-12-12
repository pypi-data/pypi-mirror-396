import torch.nn as nn


class Model_Wrapper_for_dict_in_out(nn.Module):
    """
        用于将 输入、输出是字典的模型包裹为 tuple in tuple out 的标准模型以便进行模型转换
    """

    def __init__(self, model, input_names=None, output_names=None):
        super().__init__()
        self.input_names = input_names
        self.output_names = output_names
        self.model = model

    def forward(self, *args):
        if self.input_names is not None:
            x = {k: v for k, v in zip(self.input_names, args)}
        else:
            x = args[0]
        #
        res = self.model(x)
        if self.output_names is not None:
            res = tuple(res[k] for k in self.output_names)
        return res
