import os
from kevin_toolbox.data_flow.file import json_
from kevin_toolbox.nested_dict_list import value_parser
from kevin_toolbox.nested_dict_list import serializer
import kevin_toolbox.nested_dict_list as ndl


def load_config(file_path=None, file_obj=None, update_part_s=None, b_parse_ref=True, b_force=False):
    """
        从 json 文件中读取配置

        参数：
            file_path:          <path> 文件路径
                                    支持 json 格式和 kevin_ndl 序列化格式
            file_obj:           <IO> 文件实例，要求支持通过对其调用 .read() 进行文件内容的读取。
                        以上两参数仅需指定其一即可。
            update_part_s:      <dict> 需要修改的部分
                                    是以 name 为键，value 为值的字典，其意义为将 cfg 中 name 指向的位置修改为 value。
                                    默认为 None，不进行修改
            b_parse_ref:        <boolean> 是否解释并替换配置中的引用值
                                    什么是引用值？
                                        配置文件是一个嵌套字典列表，对于其中的键值对中的值，若其为字符串类型，
                                        且其中含有 "...<cfg>{:xxx}..." 的形式，则表示一个引用。
                                        意味着读取该值时，需要将这部分替换为配置的 xxx 对应的值。
                                    默认为 True
            b_force:            <boolean> 当 update_part_s 中指向的位置不存在时，是否强制插入。
                                    默认为 False
        处理流程：
            先根据 file_path 读取文件内容 ==> 根据 update_part_s 修改内容 ==> 当 b_parse_ref=True 时把内容中带 cfg 标志的引用进行替换
    """
    if file_obj is not None:
        cfg = file_obj.read()
    else:
        assert file_path is not None
        if os.path.isfile(file_path) and file_path.endswith(".json"):
            cfg = json_.read(file_path=file_path, b_use_suggested_converter=True)
        else:
            cfg = serializer.read(input_path=file_path)

    if update_part_s is not None:
        for name, value in update_part_s.items():
            cfg = ndl.set_value(var=cfg, name=name, value=value, b_force=b_force)

    if b_parse_ref:
        # 替换引用值
        cfg, _ = value_parser.parse_and_eval_references(var=cfg, flag="cfg")
    return cfg
