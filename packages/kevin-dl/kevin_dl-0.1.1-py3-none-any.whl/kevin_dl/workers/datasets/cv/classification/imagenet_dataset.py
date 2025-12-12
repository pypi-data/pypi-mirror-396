import os
import copy
from collections import defaultdict
import warnings
from PIL import Image
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from kevin_toolbox.data_flow.file import kevin_notation
from kevin_toolbox.computer_science.algorithm import parallel_and_concurrent as pc
from kevin_toolbox.computer_science.data_structure import Executor
from kevin_dl.workers.transforms import Pipeline
from kevin_dl.workers.transforms.for_images.utils import Image_Format, get_format, convert_format
from kevin_dl.workers.datasets.utils.variable import Task_Type
from kevin_dl.workers.variable import DATASETS
from kevin_dl.utils.ceph import read_image, read_file


@DATASETS.register(name=":cv:classification:Imagenet_Dataset")
class Imagenet_Dataset(Dataset):
    """
        读取 imagenet 格式的数据集
            注意！！ 与 :cv:Image_Dataset 不同，本数据集默认以 BGR 顺序读取图片
            并且由于之前已用此数据集训练过若干模型，为兼容旧版本，仍然保留该模块，但是后续将不再修改，请改用 :cv:Image_Dataset
    """

    def __init__(self, **kwargs):
        """
            参数：
                ann_path:                       <path> 标注文件，记录有图片路径、标签等信息
                                                    支持两种格式：
                                                        - .kvt  要求至少包含键为 "image_path" 的列
                                                        - .txt  要求以空格' '作为分隔符，第一列为 image_path，第二列为 label
                prefix:                         <path> 图片路径前缀。若不指定则默认为空 ""
                            默认 ann_path 和 prefix 都在本地，若要使用 ceph，请在路径前加上 "<ceph>" 前缀
                transforms:                     <dict> 定义数据处理流程
                                                    构建 Pipeline 的设置，具体参考 workers.transforms.Pipeline
                b_bgr_order:                    <boolean> 是否按照 BGR 顺序读取图片
                                                    默认为 True，亦即使用 BGR 方式。
                output_contents:                <list of str> 需要添加到输出中的内容。
                                                    目前支持：
                                                        # 图像
                                                        "raw"  原始图像
                                                        "fin" 经过 transforms 处理后的图像
                                                        # 标签
                                                        其他保存在标注文件中的列
                task_type:                      <str> 任务类型，有 "train" "test" "val" 可选
                                                    当设置为 "train" 时，每次调用 __getitem__(idx) 生成的数据都是随机的，即使 idx 一样也可能不同。
                                                    当设置为其他时，blur 中的随机种子将在每次调用 __getitem__(idx) 时被设置为
                                                        idx+seed，以保证相同 idx 下生成的数据是相同的。
                                                    默认设置为 "train"。
                seed:                           <int>  在生成测试数据时，亦即 task_type="train" 时将模糊操作的随机种子固定为
                                                    seed + index 以保证每次生成的测试数据都是一致的。
                b_check_data_available:         <boolean> 是否在初始化阶段检查数据的可用性。
                                                    默认为 False，
                                                    由于耗时较长，仅建议在构建 configs 时进行检查。

            数据处理流程：
                raw ==> (transforms) ==> fin

            返回：
                res:            <dict> 内容依据 output_contents 而定
        """
        super().__init__()

        # 废弃警告
        warnings.warn(":cv:classification:Imagenet_Dataset 已废弃，请改用 :cv:Image_Dataset",
                      category=DeprecationWarning)

        # 默认参数
        paras = {
            # 数据集
            "ann_path": None,
            "prefix": None,
            # 数据处理
            "transforms": None,
            "b_bgr_order": True,
            "task_type": "train",
            "seed": 114514,
            # 输出
            "output_contents": ("fin", "image_path", "label"),
            #
            "b_check_data_available": False
        }

        # 获取参数
        paras.update(kwargs)

        # 校验参数
        for k in ("ann_path", "prefix"):
            if not paras[k].startswith("<ceph>"):
                paras[k] = os.path.abspath(os.path.expanduser(paras[k].strip()))  # 替换家目录
                assert os.path.exists(paras[k])
        assert isinstance(paras["transforms"], (dict,))

        # 读取数据
        content = read_file(file_path=paras["ann_path"])
        self.data_s = defaultdict(list)
        if paras["ann_path"].endswith(".txt"):
            for i in content.strip().split('\n', -1):
                temp = i.strip().split(" ", 1)
                self.data_s["image_path"].append(os.path.join(paras["prefix"], temp[0].strip()))
                self.data_s["label"].append(int(temp[1].strip()))
        elif paras["ann_path"].endswith(".kvt"):
            from io import StringIO
            _, self.data_s = kevin_notation.read(file_obj=StringIO(initial_value=content))
            assert "image_path" in self.data_s
        else:
            raise NotImplemented(f'not support {paras["ann_path"].split(".")[-1]} file')

        # check
        if paras["b_check_data_available"]:
            def func(v):
                try:
                    read_image(file_path=v)
                    return True
                except:
                    return False

            res_ls, _ = pc.multi_thread_execute(
                executors=[Executor(func=func, args=[i]) for i in self.data_s["image_path"]],
                thread_nums=5, b_display_progress=True
            )
            assert all(res_ls), \
                f'images not found:\n\t' + "\n\t".join(
                    [self.data_s["image_path"][i] for i, v in enumerate(res_ls) if not v])

        # 构建 pipeline
        self.pipeline = Pipeline(**paras["transforms"])
        self.pipeline.set_rng(seed=paras["seed"], b_delayed_set_rng=True, b_seed_wrt_worker_id=True)

        self.paras = paras

    def __len__(self):
        return len(self.data_s["image_path"])

    def __getitem__(self, idx):
        if Task_Type(self.paras["task_type"]) is not Task_Type.Train:
            self.pipeline.set_rng(seed=self.paras["seed"] + idx if self.paras["seed"] is not None else idx,
                                  b_delayed_set_rng=False, b_seed_wrt_worker_id=False)

        temp_s = dict()
        temp_s["raw"] = read_image(file_path=self.data_s["image_path"][idx], b_bgr_order=self.paras["b_bgr_order"])
        temp_s["fin"] = self.pipeline(input_s=dict(image=copy.deepcopy(temp_s["raw"])))["image"]

        res = {k: v[idx] for k, v in self.data_s.items()}
        res.update(temp_s)
        res = {k: res.get(k, None) for k in self.paras["output_contents"]}
        for k in res.keys():
            if get_format(res[k]) is Image_Format.PIL_IMAGE:
                res[k] = convert_format(res[k], input_format=Image_Format.PIL_IMAGE,
                                        output_format=Image_Format.NP_ARRAY)

        return res
