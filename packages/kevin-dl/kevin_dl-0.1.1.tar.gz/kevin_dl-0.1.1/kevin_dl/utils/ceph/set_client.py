import os
import warnings


def set_client(cfg_path, name):
    if cfg_path is None:
        return
    try:
        from petrel_client.client import Client
    except:
        warnings.warn("petrel_client is not installed, please install it")
        # raise ImportError("please install petrel_client")
    try:
        # 默认情况下，MC 所支持 key 的最大长度为250个字节。如果路径过长，将会出现 McKeySizeExceed 错误。
        #   需要用户定义 key 的转换规则来避免该错误。
        client = Client(os.path.expanduser(cfg_path), mc_key_cb="sha256")
    except:
        client = None
    from kevin_dl.utils.ceph.variable import CLIENTS
    CLIENTS.add(obj=client, name=name, b_force=True, b_execute_now=False)


def set_default_client(cfg_path):
    set_client(cfg_path=cfg_path, name=":default")
