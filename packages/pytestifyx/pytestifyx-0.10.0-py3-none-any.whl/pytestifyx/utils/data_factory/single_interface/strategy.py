from pytestifyx.utils.data_factory.run import MakeData
from pytestifyx.utils.logs.core import log

md = MakeData()


class RuleProvider:
    rule_name = ['basic', 'name', 'ssn']


class StrategyConfig:

    def __init__(self, length_config=None, category_config='数字', category_provider=None, null_provider=None, rule_provider=None):
        if category_provider is None:
            category_provider = ['数字', '字母', '汉字', '生僻字', '空']
        if null_provider is None:
            null_provider = ['字符串', '列表', '字典']
        if length_config is None:
            length_config = [6, 9]
        self.length_config = length_config  # ['min_length', 'max_length']  # 可以是一个数字，也可以是一个列表，表示可以是一个范围内的随机数
        self.category_config = category_config  # ['数字', '字母', '汉字', '生僻字', '空']  # 数字, 字母, 汉字, 生僻字，空
        self.null_provider = null_provider
        self.category_provider = category_provider
        self.rule_provider = rule_provider


class Strategy(StrategyConfig):

    def gen_field_response(self, field, config: StrategyConfig):
        response = self.gen_response(config)
        return ({field: item} for item in response)

    def gen_response(self, config: StrategyConfig):
        response = []
        # 生成长度边界值，同时类型满足规则
        if isinstance(config.length_config, list):  # 传列表则参数长度为范围区间
            log.info('参数长度为范围区间' + str(config.length_config[0]) + '-' + str(config.length_config[1]))
            response.append(md.basic(config.category_config, config.length_config[0], config.length_config[1]))
            response.append(md.basic(config.category_config, config.length_config[0]))
            response.append(md.basic(config.category_config, config.length_config[1]))
            response.append(md.basic(config.category_config, config.length_config[0] - 1))
            response.append(md.basic(config.category_config, config.length_config[1] + 1))
        if isinstance(config.length_config, str) or isinstance(config.length_config, int):
            log.info('参数长度为固定值' + str(config.length_config))
            response.append(md.basic(config.category_config, config.length_config))
            response.append(md.basic(config.category_config, int(config.length_config) - 1))
            response.append(md.basic(config.category_config, int(config.length_config) + 1))

        # 生成长度满足规则，同时类型覆盖配置值
        for category in config.category_provider:
            if category == '空':
                for i in config.null_provider:
                    response.append(md.basic(category, 0, 0, i))
            elif category == config.category_config:  # 长度边界值时已经对该类型做过遍历，需要排除
                pass
            else:  # 不为空的情况
                if isinstance(config.length_config, list):  # 传列表则参数长度为范围区间
                    response.append(md.basic(category, config.length_config[0], config.length_config[1]))
                if isinstance(config.length_config, str) or isinstance(config.length_config, int):
                    response.append(md.basic(category, config.length_config))
        if config.rule_provider:
            response.append(config.rule_provider)
        return (item for item in response)


if __name__ == '__main__':
    from faker import Faker

    fake = Faker("zh-CN")
    template = {
        "mch_id": "302207190000043504",  # 商户号
        "sub_mchid": "602202200000014203",  # 子商户编号
        "card_no": f'6222625295206' + str(fake.random_number(6)),
        "user_id": str(fake.random_number(12)),  # 用户唯一编号
        "id_no": fake.ssn(),  # 证件号码
        "acct_name": fake.name(),  # 姓名
        "bind_phone": fake.phone_number(),  # 绑定手机号
    }
    s = Strategy()
    data = s.gen_field_response('user_id')
    for i in data:
        print(i)
    # data = s.gen_body_response('user_id', template, StrategyConfig(length_config=[6, 9], category_config='数字'))
    # for i in data:
    #     print(i)
