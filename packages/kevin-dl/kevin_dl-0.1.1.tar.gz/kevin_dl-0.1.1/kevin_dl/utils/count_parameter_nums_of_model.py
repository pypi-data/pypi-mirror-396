def count_parameter_nums_of_model(model):
    res = dict(total=0, trainable=0)
    for p in model.parameters():
        res["total"] += p.numel()
        if p.requires_grad:
            res["trainable"] += p.numel()
    return res
