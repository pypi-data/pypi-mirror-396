import os


def walk(path, client=":default"):
    """
        使用 client 遍历 path 指向的目录

        参数：
            path:                   <str> 要遍历的目录
                                        读取规则：
                                            - 当 file_path 有前缀为 <ceph>，或者本地不存在该目录时，将使用 ceph 进行遍历
                                            - 否则在本地遍历目录
            client:                 <object> 客户端接口实例

        返回:
            root, dirs, files
    """
    if isinstance(client, (str,)):
        from kevin_dl.utils.ceph.variable import CLIENTS
        client = CLIENTS.get(name=client, default=None)
    #
    if path.startswith("<ceph>") and client is not None:
        yield from _walk_by_ceph(path=path[6:], client=client)
    elif not os.path.isdir(path) and client is not None:
        yield from _walk_by_ceph(path=path, client=client)
    else:
        yield from _walk_by_local(path=path)


def _walk_by_ceph(path, client):
    assert client.isdir(path), f'{path} is not a directory'
    dir_ls = [path]
    while True:
        path = dir_ls.pop(0)
        root, dirs, files = _list_dir_by_ceph(path=path, client=client)
        yield root, dirs, files
        dir_ls.extend([os.path.join(root, dir_) for dir_ in dirs])
        if len(dir_ls) == 0:
            break


def _list_dir_by_ceph(path, client):
    contents = client.list(path)
    dirs, files = [], []
    for content in contents:
        if content.endswith('/'):
            dirs.append(content)
        else:
            files.append(content)
    return path, dirs, files


def _walk_by_local(path):
    assert os.path.isdir(path), f'{path} is not a directory'
    for root, dirs, files in os.walk(path):
        yield root, dirs, files


if __name__ == '__main__':
    for root, dirs, files in walk(path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        print(root, dirs, files)
