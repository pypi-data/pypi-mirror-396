def parse_func(func):
    func = eval(func[6:]) if isinstance(func, (str,)) else func  # 对于 <eval> 开头的字符串，将其转换为函数
    assert callable(func)
    return func
