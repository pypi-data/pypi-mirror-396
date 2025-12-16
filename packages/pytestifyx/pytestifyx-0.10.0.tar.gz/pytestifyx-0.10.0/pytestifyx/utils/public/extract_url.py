import re


def extract_url(url):
    pattern = re.compile(r'<(.*?)>')
    matches = pattern.findall(url)
    return {match: match for match in matches}


def restore_url(url_template, params):
    for key, value in params.items():
        url_template = url_template.replace('<' + key + '>', value)
    return url_template


if __name__ == '__main__':
    url = "/catalog/info/del/<ids1>/<ids2>"
    print(extract_url(url))
    params = {'ids1': 'ids1', 'ids2': 'ids2'}
    url_template = "/catalog/info/del/<ids1>/<ids2>"
    print(restore_url(url_template, params))
