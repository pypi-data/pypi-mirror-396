from torch import nn
import torch
import torch.nn.functional as F
from .utils import parse_weight_config


class Mean_Adjustable_Variance_Loss(nn.Module):

    def __init__(self, **kwargs):
        super().__init__()
        paras = {
            "labels_len": 100,
            "labels_cfg_ls": [{
                "range": (None, None),
                "func": "<eval>lambda idx_ls: idx_ls",
            }],
            #
            "lambda_s": {
                "for_mean": 0.2,
                "for_var": 0.05,
                "for_adjustable_var": None
            },
            "reduction": "mean"
        }
        paras.update(kwargs)

        self.labels = torch.tensor(
            data=parse_weight_config(cfg_ls=paras["labels_cfg_ls"], weights_len=paras["labels_len"], b_normalize=False),
            dtype=torch.float32, requires_grad=False
        )
        self.lambda_adj_v = None
        if paras["lambda_s"].get("for_adjustable_var", None) is not None:
            self.lambda_adj_v = torch.tensor(
                data=parse_weight_config(
                    cfg_ls=paras["lambda_s"]["for_adjustable_var"]["cfg_ls"],
                    weights_len=paras["labels_len"], b_normalize=True,
                    temperature=paras["lambda_s"]["for_adjustable_var"]["temperature"]) * paras["labels_len"],
                dtype=torch.float32, requires_grad=False
            )

        self.paras = paras
        self._state = dict()

    def forward(self, pred, target):
        """
            参数:
                pred:           [bz, class_nums]
                target:         [bz, (1)]
        """
        target = target.type(torch.FloatTensor).view(-1).to(device=pred.device)
        self.labels = self.labels.to(device=pred.device)

        #
        prob = F.softmax(pred, dim=-1)
        pred = torch.squeeze((prob * self.labels).sum(1, keepdim=True), dim=-1)
        # mean loss
        mean_loss = (pred - target) ** 2 / 2.0
        # adjustable variance loss
        var_loss = (prob * (self.labels[None, :] - pred[:, None]) ** 2).sum(-1, keepdim=False)
        if self.lambda_adj_v is not None:
            var_loss = self.lambda_adj_v.to(device=pred.device)[target.to(dtype=int)] * var_loss

        if self.paras["reduction"] == 'sum':
            mean_loss, var_loss = mean_loss.sum(), var_loss.sum()
        else:
            mean_loss, var_loss = mean_loss.mean(), var_loss.mean()

        loss = self.paras["lambda_s"]["for_mean"] * mean_loss + self.paras["lambda_s"]["for_var"] * var_loss

        self._state = {
            "mean_loss": mean_loss.item(),
            "var_loss": var_loss.item(),
            "loss": loss.item()
        }

        return loss

    @property
    def state(self):
        return self._state


if __name__ == "__main__":
    mav = Mean_Adjustable_Variance_Loss(
        labels_len=9,
        lambda_s={
            "for_mean": 0.2,
            "for_var": 0.05,
            "for_adjustable_var": {
                "cfg_ls": [
                    {
                        "range": (0, 14),
                        "func": "<eval>lambda idx_ls: np.linspace(0.4,2.2,len(idx_ls)+1)[:-1]",
                    },
                    {
                        "range": (14, 40),
                        "func": "<eval>lambda idx_ls: np.linspace(2.2,5,len(idx_ls)+1)[:-1]",
                    },
                    {
                        "range": (40, 100),
                        "func": "<eval>lambda idx_ls: np.linspace(5,6.2,len(idx_ls)+1)[:-1]",
                    },
                    {
                        "range": (100, None),
                        "func": "<eval>lambda idx_ls: [6.2]*len(idx_ls)",
                    },
                ],
                "temperature": 5.0
            }
        }
    )
    # print(mav.labels)
    # 当 for_adjustable_var=None 时，期望 mean_loss=0.1689 var_loss=6.3688

    pred_ = torch.tensor(
        [
            [0.1, 0.2, 0.3, 0.4, 0.3, 0.2, 0.1, 0.1, 0.1],
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.1, 0.3, 0.7],
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        ], device="cuda"
    )
    target_ = torch.tensor([3.0, 4.0, 5.0], dtype=int, device="cuda")
    mav.cuda()
    print(mav(pred_, target_))
    print(mav.state)
