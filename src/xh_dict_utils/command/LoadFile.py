import argparse
import json
import os
import sys
import yaml
from xh_dict_utils.command.CommandTemplate import CommandTemplate
from xh_dict_utils.supports.SupportedFormat import SupportedFormat


class LoadFile(CommandTemplate):
    def __init__(self):
        super().__init__("load-file", "load file")

    def parserOp(self, parser: argparse.ArgumentParser):
        parser.add_argument("--format", choices=["json", "yaml"], default="yaml")
        parser.add_argument("--file")

    def handleOp(self, argv: [str]):
        format = getattr(SupportedFormat, argv.format.upper())

        def read_all_in_file(filePath) -> str:
            if not os.path.exists(filePath):
                raise Exception(f"Path[{filePath}] not exists")

            if not os.path.isfile(filePath):
                raise Exception(f"Path[{filePath}] is not file")
            with open(filePath, "r") as f:
                return f.read()

        data = read_all_in_file(argv.file)
        d = dict() if data == "" else json.loads(data)

        def printDict(d: dict):
            if format == SupportedFormat.YAML:
                return yaml.dump(d, sys.stdout)
            elif format == SupportedFormat.JSON:
                return json.dump(d, sys.stdout)
            else:
                raise Exception("Not supported format")

        printDict(d)
