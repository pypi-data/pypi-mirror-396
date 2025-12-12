import os
from kevin_dl.models.api.utils.variable import setting_s

model_s = dict()


def parse_model_name(model_name):
    global model_s
    if model_name in model_s:
        return model_s[model_name]

    if os.path.isdir(model_name):
        model_path = model_name
    else:
        models_dir_ls = setting_s["models_dir"] if isinstance(setting_s["models_dir"], list) else [
            setting_s["models_dir"]]
        for i in models_dir_ls:
            model_path = os.path.join(i, model_name)
            if os.path.isdir(model_path):
                break
        else:
            raise FileNotFoundError(f"model_name: {model_name} not found")

    model_s[model_name] = dict(
        model_path=model_path,
        model_name=model_name
    )

    return model_s[model_name]
