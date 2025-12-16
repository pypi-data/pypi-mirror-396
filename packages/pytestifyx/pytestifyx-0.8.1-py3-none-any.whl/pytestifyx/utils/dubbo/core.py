import telnetlib
from pytestifyx.utils.logs.core import log


class Dubbo(telnetlib.Telnet):
    prompt = 'dubbo>'
    coding = 'utf-8'

    def __init__(self, host=None, port=0):
        super().__init__(host, port)
        log.info(f'dubbo接口{host}:{port}连接')
        self.write(b"\n")

    def command(self, flag, str_=""):
        data = self.read_until(flag.encode())
        self.write(str_.encode() + b"\n")
        return data

    def invoke(self, service_name, method_name, arg):
        command_str = "invoke {0}.{1}({2})".format(service_name, method_name, arg)
        log.info(command_str)
        self.command(Dubbo.prompt, command_str)
        data = self.command(Dubbo.prompt)
        data = data.decode(Dubbo.coding, errors='ignore').split('\n')[0].strip()
        return data
