class GetHashCode:
    """
    返回一个字符串的hash值
    """

    def convert_n_bytes(self, n, b):
        bits = b * 8
        return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)

    def convert_4_bytes(self, n):
        return self.convert_n_bytes(n, 4)

    @classmethod
    def get_hash_code(cls, s):
        h = 0
        n = len(s)
        for i, c in enumerate(s):
            h = h + ord(c) * 31 ** (n - 1 - i)
        return cls().convert_4_bytes(h)


def hash_code(s):
    """
    :param s: str
    :return: int
    """
    hash_code_ = abs(GetHashCode.get_hash_code(str(s)))
    return hash_code_
