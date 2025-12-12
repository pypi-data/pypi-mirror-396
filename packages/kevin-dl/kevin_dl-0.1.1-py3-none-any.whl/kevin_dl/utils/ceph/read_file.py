import os


def read_file(file_path, client=":default", b_ignore_error=False):
    """
        使用 client 读取 file_path 指向的文件内容

        参数：
            file_path:              <str> 文件路径
                                        读取规则：
                                            - 当 file_path 有前缀为 <ceph>，或者本地不存在该文件时，将使用 ceph 进行读取
                                            - 否则读取本地文件
            client:                 <object> 客户端接口实例
            b_ignore_error:         <boolean> 当读取失败时是否不报错而直接返回 None
                                        默认为 False
    """
    if isinstance(client, (str,)):
        from kevin_dl.utils.ceph.variable import CLIENTS
        client = CLIENTS.get(name=client, default=None)

    if b_ignore_error:
        try:
            res = _read_file(file_path=file_path, client=client)
        except:
            res = None
    else:
        res = _read_file(file_path=file_path, client=client)
    return res


def _read_file(file_path, client):
    if file_path.startswith("<ceph>") and client is not None:
        res = _read_by_ceph(file_path=file_path[6:], client=client)
    elif not os.path.isfile(file_path) and client is not None and not file_path.startswith(("/", ".")):
        res = _read_by_ceph(file_path=file_path, client=client)
    else:
        res = _read_by_local(file_path=file_path)
    return res


def _read_by_ceph(file_path, client):
    text_bytes = client.get(file_path)
    assert text_bytes is not None, f'file {file_path} not found in ceph'
    return str(memoryview(text_bytes), encoding='utf-8')


def _read_by_local(file_path):
    assert os.path.isfile(file_path), f'file {file_path} not found in local'
    with open(file_path, "r") as f:
        content = f.read()
    return content


if __name__ == '__main__':
    from kevin_dl.utils.ceph import set_default_client

    set_default_client(cfg_path="~/petreloss.conf")

    file_url = "aoss_sco_b:s3://face-id/temp/hello.json"
    content = read_file(file_path=file_url, b_ignore_error=True)
