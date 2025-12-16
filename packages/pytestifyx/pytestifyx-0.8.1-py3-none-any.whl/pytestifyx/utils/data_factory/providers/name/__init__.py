from collections import OrderedDict

from .. import BaseProvider


class Provider(BaseProvider):
    first_names_male = [
        "伟", "强", "磊", "晓洋", "勇", "军", "杰", "鸿涛", "超", "明", "刚", "平", "辉", "鹏", "建华", "飞",
        "鑫", "文波", "斌", "宇", "浩", "红霞", "健", "俊俊", "帆", "建平", "旭", "宁", "龙", "林", "欢",
        "阳", "建华", "亮", "建", "峰", "建国", "建军", "晨", "瑞", "志强", "兵", "雷", "东", "博",
    ]
    first_names_female = [
        "芳", "娜", "敏", "静", "秀英", "丽", "艳", "娟", "霞", "秀兰", "燕", "玲", "丹", "萍",
        "红", "玉兰", "桂兰", "英", "梅", "莉", "秀珍", "婷", "玉梅", "玉珍", "凤英", "晶", "玉英", "颖",
        "雪", "慧", "红梅", "倩", "琴", "兰英", "畅", "云", "洁", "柳", "淑珍", "莹", "海燕", "冬梅",
    ]
    first_names = first_names_male + first_names_female
    last_names = OrderedDict((
        ('王', 7.170), ('李', 7.000), ('张', 6.740), ('刘', 5.100), ('陈', 4.610), ('杨', 3.220), ('黄', 2.450),
        ('吴', 2.000), ('赵', 2.000), ('周', 1.900), ('徐', 1.450), ('孙', 1.380), ('马', 1.290), ('朱', 1.280),
        ('胡', 1.160), ('林', 1.130), ('郭', 1.130), ('何', 1.060), ('高', 1.000), ('罗', 0.950), ('郑', 0.930),
        ('梁', 0.850), ('谢', 0.760), ('宋', 0.700), ('唐', 0.690), ('许', 0.660), ('邓', 0.620), ('冯', 0.620),
        ('韩', 0.610), ('曹', 0.600), ('曾', 0.580), ('彭', 0.580), ('萧', 0.560), ('蔡', 0.530), ('潘', 0.520)
    ))

    def name(self, gender='female'):
        if gender.upper() == 'MALE':
            return self.last_name() + self.first_name_male()
        elif gender.upper() == 'FEMALE':
            return self.last_name() + self.first_name_female()

    def first_name_male(self):
        return self.random_element(self.first_names_male)

    def first_name_female(self):
        return self.random_element(self.first_names_female)

    def last_name(self):
        return self.random_element(self.last_names)
