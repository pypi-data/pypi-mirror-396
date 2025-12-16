import time

from pytestifyx.utils.data_factory.single_interface.strategy import StrategyConfig, Strategy
from faker import Faker


class GeneratorField:
    def __init__(self):
        self.s = Strategy()
        self.fake = Faker("zh-CN")

    def generator_random_id(self, filed_name='user_id', length_config=32):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=length_config, null_provider=['字符串']))

    def generator_txn_time(self):
        return self.s.gen_field_response('txn_time', StrategyConfig(length_config=14, null_provider=['字符串'], rule_provider=time.strftime("%Y%m%d%H%M%S", time.localtime())))

    def generator_notify_url(self):
        return self.s.gen_field_response('notify_url', StrategyConfig(length_config=512, null_provider=['字符串'], rule_provider='https://www.baidu.com'))

    def generator_json_info(self, filed_name='basic_info'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=32, category_provider=['空'], null_provider=['字典']))

    def generator_phone(self, filed_name='reg_phone'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=11, null_provider=['字符串'], rule_provider=self.fake.phone_number()))

    def generator_name(self, filed_name='user_name'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=85, category_config='汉字', null_provider=['字符串'], rule_provider=self.fake.name()))

    def generator_enums(self, filed_name='id_type', length_config=6, rule_provider='IDCARD'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=length_config, category_config='字母', category_provider=['字母', '空'], null_provider=['字符串'], rule_provider=rule_provider))

    def generator_id_no(self, filed_name='id_no'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=32, null_provider=['字符串'], rule_provider=self.fake.ssn()))

    def generator_id_date(self, filed_name='id_date', rule_provider='2023-08-21'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=10, null_provider=['字符串'], rule_provider=rule_provider))

    def generator_address(self):
        return self.s.gen_field_response('address', StrategyConfig(length_config=85, null_provider=['字符串'], rule_provider=self.fake.address()))

    def generator_email(self, filed_name='email'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=32, null_provider=['字符串'], rule_provider=self.fake.email()))

    def generator_occupation(self):
        return self.s.gen_field_response('occupation', StrategyConfig(length_config=85, null_provider=['字符串'], rule_provider='10'))

    def generator_id_portrait(self, filed_name='id_portrait', rule_provider='123'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=85, null_provider=['字符串'], rule_provider=rule_provider))

    def generator_card_no(self, filed_name='card_no'):
        return self.s.gen_field_response(f'{filed_name}', StrategyConfig(length_config=32, null_provider=['字符串'], rule_provider=self.fake.credit_card_number()))
