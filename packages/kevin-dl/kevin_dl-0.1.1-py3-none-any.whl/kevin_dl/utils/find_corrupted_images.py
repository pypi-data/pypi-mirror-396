import os
from kevin_toolbox.data_flow.file import json_
from kevin_toolbox.computer_science.algorithm import parallel_and_concurrent as pc
from kevin_toolbox.computer_science.data_structure import Executor
from kevin_dl.utils.ceph import read_image




def read_database(database_dir=None):
    assert os.path.isdir(database_dir)
    database = dict(success=set(), fail=set(), success_new=set(), fail_new=set())
    for k in ("success", "fail"):
        v = database[k]
        if os.path.isfile(os.path.join(database_dir, f"{k}.txt")):
            with open(os.path.join(database_dir, f"{k}.txt"), 'r') as f:
                v.update(set(f.read().strip().split("\n", -1)))
    return database


def is_image_corrupted_wrapped_by_database(image_path, database):
    if image_path in database["success"]:
        b_corrupted, msg = False, "success, matches the content in the database"
    elif image_path in database["fail"]:
        b_corrupted, msg = True, "failed, matches the content in the database"
    else:
        b_corrupted, msg = is_image_corrupted(image_path)
        if b_corrupted:
            database["fail_new"].add(image_path)
        else:
            database["success_new"].add(image_path)
    return b_corrupted, msg


def is_image_corrupted(image_path, *args):
    if "s3://" not in image_path and not os.path.isfile(image_path):
        return True, "not exist"
    try:
        # 尝试读取图像文件
        img = read_image(image_path)
        if img is None:
            return True, "failed to read"
    except Exception as e:
        return True, f'{e}'

    return False, ""


def save_database(database_dir, database):
    os.makedirs(database_dir, exist_ok=True)
    for k in ("success", "fail"):
        with open(os.path.join(database_dir, f"{k}.txt"), "a") as f:
            for i in database[f'{k}_new']:
                f.write(f'{i}\n')


def find_corrupted_images(file_path_ls, output_dir, database_dir=None, prefix=None):
    """
        尝试逐一读取 file_path_ls 中的图片，并记录读取失败的部分

        参数：
            file_path_ls:           <list> 图片路径列表
            output_dir:             <path> 结果输出的目录
            database_dir:           <path> 用于缓存检查结果的数据库目录
                                        其下有 success.txt 和 fail.txt 用于保存检查过的图片路径
                                        默认为 None，此时不使用缓存结果
            prefix:                 <path> 图片路径前缀
                                        默认为 None
    """
    os.makedirs(output_dir, exist_ok=True)
    database = read_database(database_dir=database_dir)
    if prefix is not None:
        file_path_ls = [os.path.join(prefix, file_path) for file_path in file_path_ls]

    print(f'image nums: {len(file_path_ls)}')
    corrupted_images = list()  # [(data_idx, file_path, msg), ...]
    #
    func = is_image_corrupted if database is None else is_image_corrupted_wrapped_by_database
    corrupted_res_ls, failed_task_idx_ls = pc.multi_thread_execute(
        executors=[Executor(func=func, args=(file_path, database)) for file_path in file_path_ls],
        thread_nums=100, b_display_progress=True
    )
    assert len(failed_task_idx_ls) == 0
    for idx, file_path in reversed(list(enumerate(file_path_ls))):
        b_corrupted, msg = corrupted_res_ls[idx]
        if b_corrupted:
            corrupted_images.append([idx, file_path, msg])
    print(
        f'corrupted images nums:{len(corrupted_images)}(ratio: {len(corrupted_images) / len(file_path_ls) * 100:.2f}%)')

    json_.write(content=corrupted_images, file_path=os.path.join(output_dir, "corrupted_images.json"))

    if database is not None and database_dir is not None:
        save_database(database_dir=database_dir, database=database)
