def get_client(name, **kwargs):
    from kevin_dl.utils.ceph.variable import CLIENTS
    return CLIENTS.get(name=name, **kwargs)


def get_default_client():
    return get_client(name=":default")
