import re


def convert_to_type(s: str):
    """
    转换字符串为正确的数据类型

    :param s:
    :return:
    """

    if not isinstance(s, str):
        return s

    s = s.strip()  # 删除两端的空格

    # 检查字符串是否只包含数字
    if s.isdigit():
        return int(s)  # 转换为整数
    elif re.match("^\d+\.\d+$", s):
        return float(s)  # 仅有数字和小数点，则转换为浮点数
    else:
        return s  # 如果既不是纯数字也没有小数点，返回字符串本身


if __name__ == '__main__':
    res = convert_to_type('10')
    print(type(res), res)

    res = convert_to_type('10.3')
    print(type(res), res)

    res = convert_to_type('a10.3')
    print(type(res), res)
