from argparse import ArgumentParser
import sys

from pytestifyx import __description__, __version__
from pytestifyx.parse import trans_saz_to_test
from pytestifyx.scaffold import main_scaffold


def main():
    # 命令行处理程序入口
    arg_parser = ArgumentParser(description=__description__)
    arg_parser.add_argument("-V", "--version", dest="version", action="store_true", help="show version")
    arg_parser.add_argument("-P", "--project", dest="project", action="store_true", help="Create an inuyasha test project")
    arg_parser.add_argument("-T", "--parse", dest="parse", action="store_true", help="fiddler saz file parse to pytestifyx test case")

    if sys.argv[1] in ["-V", "--version"]:
        print(f"{__version__}")
    elif sys.argv[1] in ["-h", "--help"]:
        arg_parser.print_help()
    elif sys.argv[1] in ["-P", "--project"]:
        arg_parser.print_help()
        main_scaffold()
    elif sys.argv[1] in ["-T", "--parse"]:
        arg_parser.print_help()
        trans_saz_to_test()
    else:
        print(f"Unknown command: {sys.argv[1]}")
        arg_parser.print_help()
        sys.exit(0)
