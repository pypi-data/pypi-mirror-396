import os
from kevin_dl.utils.variable import root_dir

setting_s = {
    "cache_size": {k: 20 for k in ["outputs_mapper", "inputs_mapper", "pipeline", "preprocess_s", "postprocess_s"]},
    "models_dir": os.path.join(root_dir, "kevin_dl/models")
}

setting_for_kevin_sdk_s = {
    "cache_size": {k: 20 for k in ["model", ]}
}
