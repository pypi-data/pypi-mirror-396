import json
import sys
import requests

# 定义python系统变量
JOB_URL = sys.argv[1]
JOB_NAME = sys.argv[2]

# 飞书机器人的webhook地址
url = "https://open.feishu.cn/open-apis/bot/v2/hook/42d840ec-dcdc-4db7-9be0-c669d3acd155"
method = "post"
headers = {"Content-Type": "application/json"}

# 读取并解析json-report.json文件
with open("json-report.json", "r") as f:
    report = json.load(f)

# 获取summary部分的信息
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
                    "content": f"用例总数：**{total_tests}**，成功总数：**{passed_tests}**，成功率：**{success_rate}%**",
                    "tag": "lark_md",
                },
            },
            {
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "content": "查看测试报告",  # 这是卡片的按钮，点击可以跳转到url指向的allure路径
                            "tag": "lark_md",
                        },
                        "url": f"{JOB_URL}/allure/",  # JOB_URL 调用python定义的变量，该url是服务器下的allure路径
                        "type": "default",
                        "value": {},
                    }
                ],
                "tag": "action",
            },
        ],
        "header": {
            "title": {
                "content": JOB_NAME + "构建报告",  # JOB_NAME 调用python定义的变量，这是卡片的标题
                "tag": "plain_text",
            }
        },
    },
}
res = requests.request(method=method, url=url, headers=headers, json=data)
if success_rate >= 80:
    res = requests.request(method=method, url="https://open.feishu.cn/open-apis/bot/v2/hook/1341bc8e-f058-4b4a-92a0-eb0e10780749", headers=headers, json=data)
