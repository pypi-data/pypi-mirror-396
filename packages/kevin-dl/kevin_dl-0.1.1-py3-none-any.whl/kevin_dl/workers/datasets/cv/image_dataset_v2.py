import os
import copy
from io import StringIO
from PIL import Image
from torch.utils.data import Dataset
from kevin_toolbox.data_flow.file import kevin_notation, json_
from kevin_toolbox.computer_science.algorithm import parallel_and_concurrent as pc
from kevin_toolbox.computer_science.data_structure import Executor
from kevin_toolbox.computer_science.algorithm.for_seq import sample_subset_most_evenly
from kevin_dl.workers.transforms import Pipeline
from kevin_dl.workers.transforms.for_images.utils import Image_Format, get_format, convert_format
from kevin_dl.workers.datasets.utils.variable import Task_Type
from kevin_dl.workers.datasets.utils import merge_contents
from kevin_dl.workers.variable import DATASETS
from kevin_dl.utils.ceph import read_image, read_file


@DATASETS.register(name=":cv:Image_Dataset_v2:0.1")
class Image_Dataset(Dataset):
    """
        图片类通用数据集
            默认以 RGB 方式读取图片，也可以通过指定 b_bgr_order 参数来修改
            相较于旧版的 Image_Dataset，其支持以下新功能：
                1. 对每个数据集构成部分指定采样比例。
                2. 支持对数据添加指定的补充信息（tags）。
                3. 支持以执行图的方式，定义复杂的 data aug 流程。（TODO）
    """

    def __init__(self, **kwargs):
        """
            参数：
                part_s_ls:                      <list> 指定数据集的各个构成部分。
                                                    列表中每个元素应为包含以下键值对的字典：
                                                        - ann_file:     <path/list of path> 记录有图片路径、标签等信息的标注文件。
                                                                            支持以下格式：
                                                                                .kvt:       要求具有名为"image_path"的列
                                                                                .json:      格式为 [{"image_path": ..., <key_0>: ...}, ...]
                                                        - prefix:       <path/list of path> 图片路径前缀。若不指定则默认为空 ""
                                                        - sample_ratio: <float> 采样比例
                                                                            默认为 1.0
                                                        - tag_s:        <dict> 需要添加到数据的补充信息。
                filter_ls                       <list> 用于对标注文件的内容进行过滤
                                                    列表的形式为:
                                                        [
                                                            {
                                                                "args": [<key_name>, ...],
                                                                "kwargs": {<para_name>:<key_name>, ...},
                                                                "filter": <callable>  # 利用上面构造的 args 和 kwargs 作为参数的函数，返回 True 表示通过过滤
                                                            },
                                                            ...
                                                        ]
                transforms:                     <dict> 定义数据处理流程
                                                    构建 Pipeline 的设置，具体参考 workers.transforms.Pipeline
                b_bgr_order:                    <boolean> 是否按照 BGR 顺序读取图片
                                                    默认为 False，亦即使用 RGB 方式。
                output_contents:                <list of str> 需要添加到输出中的内容。
                                                    目前支持：
                                                        # 图像
                                                        "raw"  原始图像
                                                        "fin" 经过 transforms 处理后的图像
                                                        # 标签
                                                        其他保存在 kvt 文件中的列
                task_type:                      <str> 任务类型，有 "train" "test" "val" 可选
                                                    当设置为 "train" 时，每次调用 __getitem__(idx) 生成的数据都是随机的，即使 idx 一样也可能不同。
                                                    当设置为其他时，blur 中的随机种子将在每次调用 __getitem__(idx) 时被设置为
                                                        idx+seed，以保证相同 idx 下生成的数据是相同的。
                                                    默认设置为 "train"。
                seed:                           <int>  随机种子
                                                    作用：
                                                        1. 在生成测试数据时，亦即 task_type="test" 时将模糊等操作的随机种子固定为
                                                            seed + index 以保证每次生成的测试数据都是一致的。
                                                        2. 在根据 part_s_ls 构建数据集时，若需要根据 sample_ratio 进行采样，则采用该随机种子
                                                            构建的随机采样器进行采样。
                b_check_data_available:         <boolean> 是否在初始化阶段检查数据的可用性。
                                                    默认为 False，
                                                    由于耗时较长，仅建议在构建 configs 时进行检查。

            数据处理流程：
                raw ==> (transforms) ==> fin

            返回：
                res:            <dict> 内容依据 output_contents 而定
        """
        super().__init__()

        # 默认参数
        paras = {
            # 数据集
            "part_s_ls": None,
            "filter_ls": None,
            # 数据处理
            "transforms": None,
            "b_bgr_order": False,
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
        assert isinstance(paras["part_s_ls"], (list, tuple,)) and len(paras["part_s_ls"]) > 0
        assert isinstance(paras["transforms"], (dict,))

        # 读取数据
        content_ls = []
        for part_s in paras["part_s_ls"]:
            # 读取标注文件
            file_obj = StringIO(initial_value=read_file(file_path=part_s["ann_file"]))
            if part_s["ann_file"].endswith(".json"):
                content = json_.read(file_obj=file_obj)
            elif part_s["ann_file"].endswith(".kvt"):
                _, content = kevin_notation.read(file_obj=file_obj)
            else:
                raise NotImplementedError(f'Unsupported file type: {part_s["ann_file"]}')
            # 加前缀
            assert "image_path" in content
            content["image_path"] = [os.path.join(part_s.get("prefix", ""), i) for i in content["image_path"]]
            # 进行采样
            idx_ls = sample_subset_most_evenly(inputs=range(len(content["image_path"])),
                                               ratio=part_s.get("sample_ratio", 1.0),
                                               seed=paras["seed"], b_shuffle_the_tail=True)
            content = {k: [v[i] for i in idx_ls] for k, v in content.items()}
            # 添加标签
            for k, v in part_s.get("tag_s", dict()).items():
                content[k] = [v] * len(idx_ls)
            content_ls.append(content)
        self.data_s = merge_contents(content_ls=content_ls, b_exclude_columns_non_shared=True,
                                     b_exclude_rows_with_missing_value=True)

        # 过滤数据
        if paras["filter_ls"]:
            for it in paras["filter_ls"]:
                if callable(it["filter"]):
                    filter_ = it["filter"]
                elif it["filter"].startswith("<eval>"):
                    filter_ = eval(it["filter"][6:])
                else:
                    raise ValueError(f'filter not supported: {it["filter"]}')
                it.setdefault("args", list())
                it.setdefault("kwargs", dict())
                for i in reversed(list(range(len(self.data_s["image_path"])))):
                    if not filter_(*[self.data_s[k][i] for k in it["args"]],
                                   **{p_n: self.data_s[k][i] for p_n, k in it["kwargs"].items()}):
                        [v.pop(i) for v in self.data_s.values()]

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


if __name__ == '__main__':
    a = Image_Dataset(
        part_s_ls=[
            dict(
                ann_file="~/Desktop/gitlab_repos/kevin_dl/kevin_dl/workers/datasets/cv/face_liveness/Face_Liveness_from_SCC/test/test_data/data_0/annotations.kvt",
                prefix="~/Desktop/gitlab_repos/kevin_dl/kevin_dl/workers/datasets/cv/face_liveness/Face_Liveness_from_SCC/test/test_data/data_0/images",
                sample_ratio=1.5,
                tag_s=dict(dataset_name="test")
            )
        ],
        transforms={
            "settings": [
                # 添加噪声
                {
                    "name": ':for_images:torchvision:RandomGrayscale',
                    "paras": {
                        "p": 0.2
                    }
                },
                {
                    "name": ':for_images:blur:Gaussian_Blur',
                    "paras": {
                        "sigma": {
                            "p_type": "float",
                            "p_prob": "uniform",
                            "high": 1,
                            "low": 0,
                        }
                    }
                },
                #
                {
                    "name": ':for_images:torchvision:Resize',
                    "paras": {
                        "size": (224, 224)
                    }
                }
            ]
        },
        output_contents=["raw", "fin", "image_path", "label", "dataset_name"]
    )
    print(a[0])
    print(len(a))

    Image.fromarray((a[0]['raw'])).show()
    print(a[0]['fin'].shape)
