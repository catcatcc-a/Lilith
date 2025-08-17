# utils.py
from typing import Union,Any

def dict_or_list_to_str(data: Union[list,dict]) -> Any:
    """
    将字典或列表转换为格式化字符串
    Args:
        data: 待转换的字典或列表
    Returns: 格式化后的字符串
    """
    str_data = ""
    if isinstance(data, list):
        for item in data:
            str_data += item.__str__() + "\n"
        return str_data
    elif isinstance(data, dict):
        for key, value in data.items():
            str_data += f"{key}: {value.__str__()}\n"
        return str_data
    else :
        return None