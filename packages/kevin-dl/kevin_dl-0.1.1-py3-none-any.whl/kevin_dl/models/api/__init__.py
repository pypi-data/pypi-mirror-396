import onnxruntime
from kevin_toolbox.env_info import version

assert version.compare(v_0=onnxruntime.__version__, operator=">=", v_1="1.7.0"), \
    f'onnxruntime version must >= 1.7.0'

from .run_kevin_sdk_face_detect import run_kevin_sdk_face_detect
