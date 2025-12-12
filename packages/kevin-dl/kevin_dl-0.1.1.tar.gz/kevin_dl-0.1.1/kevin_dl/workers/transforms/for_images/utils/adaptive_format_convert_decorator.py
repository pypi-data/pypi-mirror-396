import functools
import kevin_toolbox.nested_dict_list as ndl
from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format, get_format


def adaptive_format_convert_decorator(accepted_format=None, p_name_accepted_format_s=None):
    """
        面向函数参数的自适应图片格式转换装饰器

        参数：
            accepted_format:            <str/ Image_Format> 函数中，image 参数需要图片的格式
            p_name_accepted_format_s:   <dict> 函数中指定位置参数需要的格式
                                            形如：
                                                {<name of para>: <accepted_format>, ...}
                                            默认为 None 不启用
    """
    if isinstance(accepted_format, (str,)):
        accepted_format = Image_Format(accepted_format)
    if isinstance(p_name_accepted_format_s, (dict,)):
        for k in p_name_accepted_format_s.keys():
            p_name_accepted_format_s[k] = Image_Format(p_name_accepted_format_s[k])

    def decorator(func):
        nonlocal accepted_format

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal accepted_format

            # 转换为函数需要的图像格式
            if accepted_format is not None:
                if "image" in kwargs:
                    kwargs["image"] = convert_format(image=kwargs["image"], output_format=accepted_format)
                else:
                    assert len(args) > 0
                    args = list(args)
                    args[0] = convert_format(image=args[0], output_format=accepted_format)
            if p_name_accepted_format_s is not None:
                temp = {"args": list(args), "kwargs": kwargs}
                for k, v in list(p_name_accepted_format_s.items()):
                    ndl.set_value(var=temp, name=k,
                                  value=convert_format(image=ndl.get_value(var=temp, name=k), output_format=v))
                args, kwargs = temp["args"], temp["kwargs"]

            # 执行
            res = func(*args, **kwargs)
            return res

        return wrapper

    return decorator
