import json
import sys
import requests

from pytestifyx.utils.parse.config import parse_yaml_config


def generate_message(job_url, job_name, report):
    """
    生成发送到飞书的消息内容
    :param job_url: 构建任务的URL
    :param job_name: 构建任务的名称
    :param report: 测试报告的JSON数据
    :return: 消息数据
    """
    summary = report["summary"]
    total_tests = summary["total"]
    passed_tests = summary.get("passed", 0)
    success_rate = passed_tests / total_tests * 100  # 计算成功率

    data = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True, "enable_forward": True},
            "elements": [
                {"tag": "hr"},  # 添加分隔线
                {
                    "tag": "div",
                    "text": {
                        "content": f"用例总数：**{total_tests}**，成功总数：**{passed_tests}**，成功率：**{success_rate:.2f}%**",
                        "tag": "lark_md",
                    },
                },
                {
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "查看测试报告",  # 卡片的按钮，点击可跳转到url指向的allure路径
                                "tag": "lark_md",
                            },
                            "url": f"{job_url}/allure/",  # JOB_URL是服务器下的allure路径
                            "type": "default",
                            "value": {},
                        }
                    ],
                    "tag": "action",
                },
            ],
            "header": {
                "title": {
                    "content": job_name + "构建报告",  # JOB_NAME是卡片的标题
                    "tag": "plain_text",
                }
            },
        },
    }
    return data


class FeishuNotifier:
    def __init__(self, config_file='config.yaml'):
        """
        初始化类并加载配置文件
        :param config_file: 配置文件路径
        """
        config = parse_yaml_config(config_file)
        self.webhook_url = config['feishu']['webhook_url']
        self.report_file_path = config['report']['file_path']

    def read_report(self):
        """
        读取并解析JSON报告文件
        :return: 报告的JSON数据
        """
        with open(self.report_file_path, 'r') as f:
            return json.load(f)

    def send_message(self, data):
        """
        发送消息到飞书
        :param data: 消息内容
        :return: 请求响应
        """
        headers = {"Content-Type": "application/json"}
        res = requests.post(url=self.webhook_url, headers=headers, json=data)
        return res

    def send_notification(self, job_url, job_name):
        """
        读取报告，生成消息并发送通知
        :param job_url: 构建任务的URL
        :param job_name: 构建任务的名称
        :return: 请求响应
        """
        report = self.read_report()
        data = generate_message(job_url, job_name, report)
        return self.send_message(data)


if __name__ == "__main__":
    JOB_URL = sys.argv[1]
    JOB_NAME = sys.argv[2]

    notifier = FeishuNotifier(config_file='config.yaml')
    response = notifier.send_notification(JOB_URL, JOB_NAME)
    print(response.status_code, response.text)
