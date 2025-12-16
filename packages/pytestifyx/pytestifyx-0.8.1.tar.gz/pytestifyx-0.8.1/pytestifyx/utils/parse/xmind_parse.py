class TestModule:
    def __init__(self, module_name, parent=None):
        self.module_name = module_name
        self.parent = parent
        self.test_cases = []

    def add_test_case(self, test_case):
        self.test_cases.append(test_case)

    def to_dict(self):
        return {
            "module_name": self.module_name,
            "parent": self.parent,
            "test_cases": [test_case.to_dict() for test_case in self.test_cases]
        }


class TestCase:
    def __init__(self, test_case_name, steps, makers=None, labels=None, note=None):
        self.test_case_name = test_case_name
        self.steps = steps
        self.makers = makers if makers is not None else []
        self.labels = labels if labels is not None else []
        self.note = note

    def to_dict(self):
        return {
            "test_case_name": self.test_case_name,
            "makers": self.makers,
            "labels": self.labels,
            "note": self.note,
            "steps": self.steps
        }


class TestStructureBuilder:
    def __init__(self, topics):
        self.topics = topics
        self.modules = {}

    def parse_topics(self, topics, path):
        for topic in topics:
            new_path = path.copy() + [topic]

            # 检查当前节点是否是预期结果
            if "预期结果" in topic['title']:
                if len(new_path) >= 4:  # 确保路径长度足够以避免 ValueError
                    module_name, test_case_name, test_step = new_path[-4]['title'], new_path[-3]['title'], new_path[-2]['title']
                    expected_result = topic['title']

                    # 从topic获取makers、labels、note
                    makers = new_path[-3].get('makers', [])
                    labels = new_path[-3].get('labels', [])
                    note = new_path[-3].get('note', '')
                    parent = new_path[-4].get('parent', '')

                    # 确保模块存在
                    if module_name not in self.modules:
                        self.modules[module_name] = TestModule(module_name, parent)

                    # 查找或创建测试用例
                    test_case = next((tc for tc in self.modules[module_name].test_cases if tc.test_case_name == test_case_name), None)
                    if not test_case:
                        test_case = TestCase(test_case_name, [], makers, labels, note)
                        self.modules[module_name].add_test_case(test_case)

                    # 查找是否存在相同的测试步骤
                    step = next((s for s in test_case.steps if s['action'] == test_step), None)
                    if step:
                        # 如果测试步骤已存在，检查预期结果是否已经存在
                        if expected_result not in step['expected_results']:
                            # 如果预期结果不存在，则向该步骤的预期结果列表中追加新的预期结果
                            step['expected_results'].append(expected_result)
                    else:
                        # 否则，创建新的测试步骤并添加预期结果
                        test_case.steps.append({
                            "action": test_step,
                            "expected_results": [expected_result]
                        })
                else:
                    raise ValueError("路径长度不足，需要包含最基本的用例名称、用例步骤、预期结果")

            elif 'children' in topic:
                # 如果当前节点不是叶节点，则继续递归
                self.parse_topics(topic['children'], new_path)

    def build(self):
        self.parse_topics(self.topics, [])
        return list(self.modules.values())

    def get_parsed_dict(self):
        modules = self.build()
        return {module.module_name: module.to_dict() for module in modules}


class Statistics:
    def __init__(self, data=None):
        self.data = data

    def count_test_cases(self):
        return self._count_test_cases_recursive(self.data)

    def _count_test_cases_recursive(self, json_data):
        count = 0
        for key, value in json_data.items():
            if key == "test_case_name":
                count += 1
            elif isinstance(value, dict):
                count += self._count_test_cases_recursive(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        count += self._count_test_cases_recursive(item)
        return count


# 定义递归函数来处理父子关系
def process_topics(topic, parent=None):
    module = {
        'title': topic['title'],
        'parent': parent,
        'children': []
    }

    if 'topics' in topic:
        for sub_topic in topic['topics']:
            child = process_topics(sub_topic, parent=module['title'])
            module['children'].append(child)

    return module


if __name__ == '__main__':
    import json
    from xmindparser import xmind_to_dict

    stats = Statistics()
    xmind_file = './xx冒烟用例.xmind'
    sheet = xmind_to_dict(xmind_file)[0]
    # print(json.dumps(sheet['topic'], indent=2, ensure_ascii=False))
    root_module = process_topics(sheet['topic'])
    # print(json.dumps(root_module, ensure_ascii=False))

    parsed_dict_generator = TestStructureBuilder(root_module['children']).get_parsed_dict()
    print(json.dumps(parsed_dict_generator, indent=2, ensure_ascii=False))
    statistics = Statistics(parsed_dict_generator).count_test_cases()
    print(statistics)
