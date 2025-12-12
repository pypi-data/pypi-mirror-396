import torch
import torch.nn.functional as F
from tqdm import tqdm
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.computer_science.algorithm.statistician import Average_Accumulator, Accumulator_for_Ndl
from kevin_toolbox.computer_science.algorithm.scheduler import Trigger
from kevin_dl.workers.metrics import cal_accuracy


class Runner:
    def __init__(self, model, data_loader, optimizer, trigger: Trigger = None, criterion=None, **kwargs):
        """
            参数：
                model:                      模型。
                data_loader:                数据 batch 生成器。
                optimizer:                  优化器。
                trigger:                    触发器。
                max_steps_per_epoch:        <int> 最多以多少个 step 作为一个 epoch。
                                                默认为 None，表示以一次完整的 data_loader 遍历作为一个 epoch。
                b_continuous_between_epochs:    <boolean> 当 max_steps_per_epoch 小于 data_loader 的大小时，
                                                后一个 epoch 的数据是否接着前一个 epoch 的结束位置继续迭代。
                                                默认为 False。
                load_next_segment_at:       <str/None> （若数据集支持segmented_loading机制，则）在什么时刻刷新数据集的下一个分块
                                                支持以下模式：
                                                    - "epoch_end":          在 epoch 结束时进行刷新
                                                    - "loader_end":         在 dataloader 迭代结束时刷新
                                                默认使用 "loader_end" 模式
                                                该参数仅在 b_continuous_between_epochs=True 时候会实际起作用（因为 False 时
                                                epoch_end 实际上也是 loader_end 了）
        """
        # 默认参数
        paras = {
            #
            "max_steps_per_epoch": None,
            "b_continuous_between_epochs": False,
            "load_next_segment_at": "loader_end",
        }

        # 获取参数
        paras.update(kwargs)

        assert paras["load_next_segment_at"] in ("epoch_end", "loader_end")

        self.model = model
        self.data_loader = data_loader
        self.data_iterator = iter(data_loader)
        self.optimizer = optimizer
        self.trigger = trigger
        self.criterion = F.cross_entropy if criterion is None else criterion
        self.paras = paras
        self.record_s = self.init_record()
        self.state_s = {
            "epoch": -1,
            "step": -1,
            "task_type": "test"
        }

    def init_record(self):
        self.record_s = {
            "loss": Average_Accumulator(),
            "total_iter_nums": 0,
            "acc_s": Accumulator_for_Ndl(accumulator_builder=Average_Accumulator)
        }
        return self.record_s

    def get_record(self, b_clear_after_read=True):
        res = self.record_s.copy()
        res = ndl.traverse(var=res, match_cond=lambda _, __, v: hasattr(v, "get") and callable(v.get),
                           action_mode="replace", converter=lambda _, v: v.get())
        if b_clear_after_read:
            self.record_s = self.init_record()
        return res

    def set_state(self, task_type=None, step=None, epoch=None, **kwargs):
        if task_type is not None:
            if task_type == "train":
                self.model.train()
            elif task_type in ("val", "test"):
                self.model.eval()
            else:
                raise ValueError
            self.state_s["task_type"] = task_type
        if step is not None:
            self.state_s["step"] = step
        if epoch is not None:
            self.state_s["epoch"] = epoch

    def run_epoch(self, **kwargs):
        self.state_s["epoch"] += 1
        if "state_s" in kwargs:
            self.set_state(**kwargs["state_s"])
        else:
            self.set_state(**kwargs)
        if self.trigger is not None:
            self.trigger.update_by_state(cur_state=self.state_s)

        max_steps_per_epoch = self.paras["max_steps_per_epoch"]
        if max_steps_per_epoch is None:
            max_steps_per_epoch = len(self.data_loader)

        if self.paras["b_continuous_between_epochs"]:
            # 创建进度条
            pbar = tqdm(total=max_steps_per_epoch, desc="Continuous Epoch Processing", mininterval=0.5)  # 降低刷新频率提升性能
            cur_step = 0
            while cur_step < max_steps_per_epoch:
                try:
                    data = next(self.data_iterator)
                except StopIteration:
                    self._loader_end()
                    self.data_iterator = iter(self.data_loader)
                    continue
                self.run_step(data, **kwargs)
                cur_step += 1
                pbar.update(1)  # 手动更新进度条
                pbar.set_postfix({"Step": f"{cur_step}/{max_steps_per_epoch}"})  # 实时状态
            pbar.close()  # 确保资源释放
        else:
            for cur_step, data in enumerate(
                    tqdm(self.data_loader, total=min(max_steps_per_epoch, len(self.data_loader)))):
                if cur_step >= max_steps_per_epoch:
                    break
                self.run_step(data, **kwargs)
            self._loader_end()
        self._epoch_end()

    def run_step(self, data, **kwargs):
        self.state_s["step"] += 1
        self.set_state(**kwargs)
        if self.trigger is not None:
            self.trigger.update_by_state(cur_state=self.state_s)
        self._run_step(data, **kwargs)

    def _run_step(self, data, **kwargs):
        """请依据实际逻辑需要，替换该函数"""
        if torch.cuda.is_available():
            data = ndl.traverse(var=data, match_cond=lambda _, __, v: torch.is_tensor(v), action_mode="replace",
                                converter=lambda _, v: v.cuda())
        x, y = data[0], data[1]
        # forward
        predict = self.model(x)

        # loss
        loss = self.criterion(predict, y, reduction='mean')

        # update by grads
        if self.state_s["task_type"] == "train":
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        # record
        #   postprocess
        acc_s = cal_accuracy.for_classification_task(predict=predict, target=y, top_ks_to_cal=[1, 5])
        self.record_s["acc_s"].add(acc_s)
        self.record_s["loss"].add(loss.item())
        self.record_s["total_iter_nums"] += 1

    def _loader_end(self):
        if (hasattr(self.data_loader.dataset, "load_next_segment") and
                self.paras["load_next_segment_at"] == "loader_end"):
            self.data_loader.dataset.load_next_segment()

    def _epoch_end(self):
        if (hasattr(self.data_loader.dataset, "load_next_segment") and
                self.paras["load_next_segment_at"] == "epoch_end"):
            self.data_loader.dataset.load_next_segment()
