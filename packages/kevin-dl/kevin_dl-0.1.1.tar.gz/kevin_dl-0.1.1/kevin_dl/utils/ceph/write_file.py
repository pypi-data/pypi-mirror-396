import os


def write_file(file_path, content, client=":default", encoding='utf-8'):
    """
        使用 client 将文件写入到 file_path 指向的位置

        参数：
            file_path:              <str> 文件路径
                                        读取规则：
                                            - 当 file_path 有前缀为 <ceph>，或者本地不存在该目录时，将使用 ceph 进行遍历
                                            - 否则在本地遍历目录
            content:                <str/bytes> 要写入内容
            client:                 <object> 客户端接口实例
            encoding:               <str> 若写入内容为字符串，则按照该编码解释为字节串
    """
    if isinstance(client, (str,)):
        from kevin_dl.utils.ceph.variable import CLIENTS
        client = CLIENTS.get(name=client, default=None)
    if isinstance(content, str):
        content = content.encode(encoding)
    assert isinstance(content, bytes), f'content must be bytes'
    #
    if file_path.startswith("<ceph>") and client is not None:
        _write_by_ceph(file_path=file_path[6:], client=client, content=content)
    elif not os.path.isfile(file_path) and client is not None:
        _write_by_ceph(file_path=file_path, client=client, content=content)
    else:
        _write_by_local(file_path=file_path, content=content)


def _write_by_ceph(file_path, client, content):
    client.put(file_path, content)


def _write_by_local(file_path, content):
    with open(file_path, "wb") as f:
        f.write(content)
