from kevin_dl.workers.optimizations import get_optimizer
from kevin_dl.workers.algorithms.variational_conv.test.example_model import Net
from kevin_dl.utils.scheduler import Trigger

net = Net(in_channels=3, out_channels=12, n_output=10, mode="variational")

# print(
#     get_optimizer(
#         type_="torch.optim.SGD",
#         named_parameters=net.named_parameters(),
#         setting=dict(lr=1e-3)
#     )
# )

opt = get_optimizer(
    type_="torch.optim.Adam",
    named_parameters=net.named_parameters(),
    setting=dict(lr=1e-3, betas=[0.9, 0.999]),
    setting_for_groups={"vc_basic": dict(lr=0)},
    # 策略
    strategy_for_vc={
        "__dict_form": "trigger_value:para_name",
        "__trigger_name": "epoch",
        "<f>lambda x: x%100==0": dict(
            setting_for_groups={"vc_basic": dict(lr=dict(set_to=0.1))},
        ),
    },
    strategy_for_all={
        "__dict_form": "trigger_value:para_name",
        "__trigger_name": "epoch",
        "<f>lambda x: x%300==0": dict(
            setting=dict(betas=[dict(multiply_by=0.1), None], lr=dict(set_to=10)),
        ),
    },
)
print(opt)

trigger = Trigger()
trigger.bind(target=opt.update)
trigger.update(cur_state=dict(epoch=1, step=1))
print(opt)

trigger.update(cur_state=dict(epoch=300, step=1))
print(opt)
