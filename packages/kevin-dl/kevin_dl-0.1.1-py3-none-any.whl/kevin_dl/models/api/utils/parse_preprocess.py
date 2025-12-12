import os
from kevin_toolbox.computer_science.algorithm.cache_manager import Cache_Manager
from kevin_toolbox.data_flow.file import json_
from kevin_dl.workers.transforms import Pipeline
from kevin_dl.models.api.utils import import_function_from_file
from kevin_dl.models.api.utils.variable import setting_s

preprocess_s_cache = Cache_Manager(upper_bound=setting_s["cache_size"]["preprocess_s"])
pipeline_cache = Cache_Manager(upper_bound=setting_s["cache_size"]["pipeline"])
inputs_mapper_cache = Cache_Manager(upper_bound=setting_s["cache_size"]["inputs_mapper"])


def parse_preprocess(model_name, model_path):
    """
        解读模型下的 preprocess.json 文件，并构建：
            - pipeline：                         用于数据前处理
            - inputs_mapper（可选，建议使用）：       用于将处理完的数据转换为推理模型时可以接受的输入格式
    """
    if not preprocess_s_cache.has(key=model_name):
        preprocess_s = json_.read(file_path=os.path.join(model_path, "preprocess.json"), b_use_suggested_converter=True)
        preprocess_s.setdefault("b_bgr_image", False)
        preprocess_s.setdefault("inputs_mapper", None)
        preprocess_s_cache.add(
            key=model_name,
            value=preprocess_s
        )
    preprocess_s = preprocess_s_cache.get(key=model_name)

    if not pipeline_cache.has(key=model_name):
        pipeline_cache.add(
            key=model_name,
            value=Pipeline(**preprocess_s["pipeline"])
        )
    preprocess_s["pipeline"] = pipeline_cache.get(key=model_name)

    if preprocess_s["inputs_mapper"] is not None:
        if not inputs_mapper_cache.has(key=model_name):
            inputs_mapper_cache.add(
                key=model_name,
                value=import_function_from_file(
                    file_path=os.path.join(model_path,
                                           preprocess_s["inputs_mapper"]["module"]),
                    function_name=preprocess_s["inputs_mapper"]["func"]
                )
            )
        preprocess_s["inputs_mapper"] = inputs_mapper_cache.get(key=model_name)
    return preprocess_s
