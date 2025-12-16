import base64


def path2base64(path):
    """
    将图片转换为base64
    :param path: 图片路径
    :return: base64
    """
    with open(path, "rb") as f:
        byte_data = f.read()
    base64_str = base64.b64encode(byte_data).decode("ascii")  # 二进制转base64
    return base64_str
