import os


def read_folder(folder_path, client=":default"):
    """
        使用 client 读取 folder_path 指向的文件内容

        参数：
            folder_path:              <str> 文件路径
                                        读取规则：
                                            - 当 folder_path 有前缀为 <ceph>，或者本地不存在该文件时，将使用 ceph 进行读取
                                            - 否则读取本地文件
            client:                 <object> 客户端接口实例
    """
    if isinstance(client, (str,)):
        from kevin_dl.utils.ceph.variable import CLIENTS
        client = CLIENTS.get(name=client, default=None)

    if folder_path.startswith("<ceph>") and client is not None:
        res = _read_by_ceph(folder_path=folder_path[6:], client=client)
    elif not os.path.isfile(folder_path) and client is not None:
        res = _read_by_ceph(folder_path=folder_path, client=client)
    else:
        res = _read_by_local(folder_path=folder_path)
    return res


def _read_by_ceph(folder_path, client):
    contents = client.list(folder_path)
    print(contents)
    return contents


def _read_by_local(folder_path):
    assert os.path.isfile(folder_path), f'file {folder_path} not found in local'
    with open(folder_path, "r") as f:
        content = f.read()
    return content


if __name__ == '__main__':
    for root, dirs, files in read_folder(path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        print(root, dirs, files)