import os
from kevin_toolbox.computer_science.algorithm.cache_manager import Cache_Manager
from kevin_toolbox.data_flow.file import json_
from kevin_dl.models.api.utils import import_function_from_file
from kevin_dl.models.api.utils.variable import setting_s

postprocess_s_cache = Cache_Manager(upper_bound=setting_s["cache_size"]["postprocess_s"])
outputs_mapper_cache = Cache_Manager(upper_bound=setting_s["cache_size"]["outputs_mapper"])


def parse_postprocess(model_name, model_path):
    """
        解读模型下的 postprocess.json 文件，并构建：
            - outputs_mapper（可选，建议使用）：       用于对模型的输出进行后处理。
    """
    if not postprocess_s_cache.has(key=model_name):
        postprocess_s = json_.read(file_path=os.path.join(model_path, "postprocess.json"),
                                   b_use_suggested_converter=True)
        postprocess_s.setdefault("outputs_mapper", None)
        postprocess_s_cache.add(
            key=model_name,
            value=postprocess_s
        )
    postprocess_s = postprocess_s_cache.get(key=model_name)

    if postprocess_s["outputs_mapper"] is not None:
        if not outputs_mapper_cache.has(key=model_name):
            outputs_mapper_cache.add(
                key=model_name,
                value=import_function_from_file(
                    file_path=os.path.join(model_path,
                                           postprocess_s["outputs_mapper"]["module"]),
                    function_name=postprocess_s["outputs_mapper"]["func"]
                )
            )
        postprocess_s["outputs_mapper"] = outputs_mapper_cache.get(key=model_name)
    return postprocess_s
