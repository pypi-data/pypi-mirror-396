import os
import cv2
import numpy as np


def read_image(file_path, client=":default", b_bgr_order=True, b_ignore_error=False):
    """
        使用 client 读取 file_path 指向的图片
            注意！！默认以 BGR 顺序读取图片

        参数：
            file_path:              <str> 文件路径
                                        读取规则：
                                            - 当 file_path 有前缀为 <ceph>，或者本地不存在该文件时，将使用 ceph 进行读取
                                            - 否则读取本地文件
            client:                 <object> 客户端接口实例
            b_bgr_order:            <boolean> 是否按照 BGR 顺序读取
                                        默认为 True
            b_ignore_error:         <boolean> 当读取失败时是否不报错而直接返回 None
                                        默认为 False

        返回:
            <np.array>
    """
    if isinstance(client, (str,)):
        from kevin_dl.utils.ceph.variable import CLIENTS
        client = CLIENTS.get(name=client, default=None)
    if b_ignore_error:
        try:
            res = _read_image(file_path=file_path, client=client, b_bgr_order=b_bgr_order)
        except Exception as e:
            res = None
    else:
        res = _read_image(file_path=file_path, client=client, b_bgr_order=b_bgr_order)
    return res


def _read_image(file_path, client, b_bgr_order):
    if file_path.startswith("<ceph>") and client is not None:
        res = _read_by_ceph(file_path=file_path[6:], client=client)
    elif not os.path.isfile(file_path) and client is not None and not file_path.startswith(("/", ".")):
        res = _read_by_ceph(file_path=file_path, client=client)
    else:
        res = _read_by_local(file_path=file_path)
    #
    if not b_bgr_order:
        res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    return res


def _read_by_ceph(file_path, client):
    image_bytes = client.get(file_path)
    assert image_bytes is not None, f'image {file_path} not found in ceph'
    image_array = np.frombuffer(memoryview(image_bytes), np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


def _read_by_local(file_path):
    assert os.path.isfile(file_path), f'image {file_path} not found in local'
    image = cv2.imread(file_path)
    return image
