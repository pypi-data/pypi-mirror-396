import os
import torch
from kevin_toolbox.computer_science.algorithm.registration import Registry

# 导入时的默认过滤规则
ignore_s = [
    {
        "func": lambda _, __, path: os.path.basename(path) in ["temp", "test", "__pycache__",
                                                               "_old_version"],
        "scope": ["root", "dirs"]
    },
]

"""
模型
"""
TOOLS = Registry(uid="TOOLS")
TOOLS.collect_from_paths(
    path_ls=[os.path.join(os.path.dirname(__file__), "face"), ],
    ignore_s=ignore_s,
    b_execute_now=False
)
