import string

from pytestifyx.utils.logs.core import log
from .. import BaseProvider


class Provider(BaseProvider):
    chinese_words = ["伟", "强", "磊", "晓", "勇", "军", "杰", "鸿", "超", "明", "刚", "平", "辉", "鹏", "建", "飞"]
    rare_words = ["牀", "牁", "牂", "牃", "牄", "牅", "牊", "牉", "牋", "牍", "牎", "牏", "牐", "牑", "牒", "牓"]

    def basic(self, category, min_length, max_length=None, *args):
        if max_length is None:
            max_length = min_length
        return self.basic_basic(category, min_length, max_length, *args)

    def basic_basic(self, category, min_length, max_length, *args):
        min_length = int(min_length)
        max_length = int(max_length)
        if category == '数字':
            return self.basic_digit(min_length, max_length)
        elif category == '字母':
            return self.basic_alphabet(min_length, max_length)
        elif category == '汉字':
            return self.basic_chinese(min_length, max_length)
        elif category == '生僻字':
            return self.basic_rare_chinese(min_length, max_length)
        elif category == '空':
            return self.basic_null(*args)

    def get_length(self, min_length, max_length):
        data = [i for i in range(min_length, max_length + 1)]
        length = self.random_element(data)
        log.info('长度为' + str(length))
        return length

    def basic_digit(self, min_length, max_length):
        length = self.get_length(min_length, max_length)
        return ''.join([str(self.random_digit_not_null()) for i in range(length)])

    def basic_alphabet(self, min_length, max_length):
        length = self.get_length(min_length, max_length)
        return ''.join([str(self.random_element(string.ascii_letters)) for i in range(length)])

    def basic_chinese(self, min_length=6, max_length=8):
        length = self.get_length(min_length, max_length)
        return ''.join([self.random_element(self.chinese_words) for i in range(length)])

    def basic_rare_chinese(self, min_length=6, max_length=8):
        length = self.get_length(min_length, max_length)
        return ''.join([self.random_element(self.rare_words) for i in range(length)])

    def basic_null(self, *args):
        category = args[0].upper()
        print(category)
        if category == '字符串':
            return ''
        elif category == '字典':
            return {}
        elif category == '列表':
            return []
        elif category == 'SET':
            return ()
        else:
            raise Exception('请输入正确的类型')
