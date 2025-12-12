import os
from kevin_toolbox.computer_science.algorithm.registration import Registry

# 导入时的默认过滤规则
ignore_s = [
    {
        "func": lambda _, __, path: os.path.basename(path) in ["temp", "test", "__pycache__",
                                                               "_old_version"],
        "scope": ["root", "dirs"]
    },
]

CLIENTS = Registry(uid="CLIENTS")
# CLIENTS.collect_from_paths(
#     path_ls=[],
#     ignore_s=ignore_s,
#     b_execute_now=False
# )
from kevin_dl.utils.ceph import set_client

set_client(name=":default", cfg_path="~/petreloss.conf")
