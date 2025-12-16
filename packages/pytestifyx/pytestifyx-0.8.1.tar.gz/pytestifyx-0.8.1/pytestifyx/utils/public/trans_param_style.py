import re


def snake_to_lower_camel(params: dict):
    """
    将参数名的驼峰形式转为下划线形式
    :param params:dict
    :return:dict
    """
    temp_dict = {}
    for name, value in params.items():
        temp_name = ""
        if re.search("[A-Z]", name):
            capital_letters = re.findall("[A-Z]", name)
            for c in capital_letters:
                lower_c = c.lower()
                r_str = "_" + lower_c
                temp_name = name.replace(c, r_str)
        else:
            temp_name = name

        temp_dict.update({temp_name: value})

    return temp_dict


def convert_string(s):
    # 将字符串转换为大驼峰式
    return s.title().replace("_", "")
