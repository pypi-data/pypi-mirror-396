import importlib.util

def import_function_from_file(file_path, function_name):
    # 获取模块规格
    spec = importlib.util.spec_from_file_location("my_module", file_path)
    # 加载模块
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # 获取函数
    function = getattr(module, function_name, None)
    return function