import os


def download(file_path, output_dir, client=":default"):
    if isinstance(client, (str,)):
        from kevin_dl.utils.ceph.variable import CLIENTS
        client = CLIENTS.get(name=client, default=None)

    if file_path.startswith("<ceph>"):
        file_path = file_path[6:]

    bytes_ = client.get(file_path)
    assert bytes_ is not None, f'file {file_path} not found in ceph'

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, os.path.basename(file_path)), 'wb') as f:
        f.write(bytes_)
