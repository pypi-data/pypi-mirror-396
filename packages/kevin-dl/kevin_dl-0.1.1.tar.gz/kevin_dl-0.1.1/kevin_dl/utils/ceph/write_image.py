import os
import cv2


def write_image(file_path, image, client=":default", b_bgr_image=True):
    """
        使用 client 将图片写入到 file_path 指向的位置

        参数：
            file_path:              <str> 文件路径
                                        读取规则：
                                            - 当 file_path 有前缀为 <ceph>，或者本地不存在该目录时，将使用 ceph 进行写入
                                            - 否则写入到本地
            image:                  <array> 图片
            client:                 <object> 客户端接口实例
            b_bgr_image:            <boolean> 输入的图片是否按照 BGR 顺序读取
                                        默认为 True
    """
    if isinstance(client, (str,)):
        from kevin_dl.utils.ceph.variable import CLIENTS
        client = CLIENTS.get(name=client, default=None)

    if not b_bgr_image:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    #
    if file_path.startswith("<ceph>") and client is not None:
        _write_by_ceph(file_path=file_path[6:], client=client, image=image)
    elif not os.path.isdir(os.path.dirname(file_path)) and client is not None:
        _write_by_ceph(file_path=file_path, client=client, image=image)
    else:
        _write_by_local(file_path=file_path, image=image)


def _write_by_ceph(file_path, client, image):
    img_ext = os.path.splitext(file_path)[-1]
    success, image_array = cv2.imencode(img_ext, image)
    assert success, f'failed to write image to ceph({file_path})'
    image_bytes = image_array.tostring()
    client.put(file_path, image_bytes)


def _write_by_local(file_path, image):
    cv2.imwrite(file_path, image)
