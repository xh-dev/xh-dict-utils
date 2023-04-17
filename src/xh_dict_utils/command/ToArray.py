import json
import re
import sys
from typing import List

import yaml

from command.CommandTemplate import *


class ToArray(CommandTemplate):
    def __init__(self):
        super().__init__("to-list", "row data to array")

    def parserOp(self, parser: argparse.ArgumentParser):
        parser.add_argument("--regex", type=str)
        parser.add_argument("--formatting", type=str, default="{{\"{key}\": \"{value}\"}}")

    def handleOp(self, argv: List[str]):
        regex_pattern = re.compile(argv.regex)
        formatting = argv.formatting
        pairs = ",".join([
            formatting.format_map(match_result.groupdict())
            for line in sys.stdin.readlines()
            for match_result in [regex_pattern.match(line)]
            if match_result
        ])
        yaml.dump(
            json.loads(f"[{pairs}]"), sys.stdout
        )


if __name__ == '__main__':
    toArray = ToArray()
    parser = argparse.ArgumentParser(
        prog="temp"
    )
    toArray.parserOp(parser)
    argv = parser.parse_args(["--regex", "(?P<key>[^ ]+)[ ]*=[ ]*\"(?P<value>.+)\"[ ]*"])
    toArray.handleOp(argv)
