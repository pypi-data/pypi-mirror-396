import torch
import numpy as np
import onnxruntime
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.computer_science.algorithm.cache_manager import Cache_Manager

ort_session_cache = Cache_Manager(upper_bound=5)

'''
run()
args有两个参数:output_names，input
    1.output_names:tuple of string,default=None
      用来指定输出哪些，以及顺序
        若为None，则按序输出所有的output，即返回[output_0,output_1]
        若为['output_1','output_0']，则返回[output_1,output_0]
        若为['output_0']，则仅返回[output_0:tensor]
    2.input:dict
        可以通过ort_session.get_inputs()[0].name，ort_session.get_inputs()[1].name获得名称
        其中key值要求与torch.onnx.export中设定的一致。

return:返回一个由output_names指定的list
'''


def run_onnx_model(model_path, inputs, output_names=None, b_use_gpu=True):
    global ort_session_cache

    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if b_use_gpu else ['CPUExecutionProvider']
    if not ort_session_cache.has(key=(model_path, b_use_gpu)):
        ort_session_cache.add(
            key=(model_path, b_use_gpu),
            value=onnxruntime.InferenceSession(model_path, providers=providers)
        )  # 创建一个推理session
    ort_session = ort_session_cache.get(key=(model_path, b_use_gpu))

    inputs_names = [i.name for i in ort_session.get_inputs()]
    assert isinstance(inputs, (dict,)) and set(inputs.keys()).issuperset(set(inputs_names)), \
        f'expected inputs is a dict with {inputs_names}'
    ndl.traverse(var=inputs, match_cond=lambda _, __, v: torch.is_tensor(v), action_mode="replace",
                 converter=lambda _, v: v.detach().cpu().numpy())
    outputs = ort_session.run(output_names, inputs)
    return outputs


if __name__ == '__main__':
    import torch

    outputs = run_onnx_model(
        model_path="~/Desktop/gitlab_repos/kevin_dl/kevin_dl/deploy/temp/model.onnx",
        inputs={"input_0": torch.randn((1, 3, 224, 224))})
    print(outputs)
