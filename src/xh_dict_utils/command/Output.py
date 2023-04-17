import argparse
import json
import sys

import yaml

from xh_dict_utils.command.CommandTemplate import CommandTemplate
from xh_dict_utils.supports.Logger import Logger
from xh_dict_utils.supports.SupportedFormat import SupportedFormat


class Output(CommandTemplate):
    def __init__(self):
        super().__init__("output", "output as json")

    def parserOp(self, parser: argparse.ArgumentParser):
        parser.add_argument("--store", type=str, default=None)
        parser.add_argument("--format", choices=["json", "yaml"])
        parser.add_argument("--pretty", action="store_true", default=False)

    def handleOp(self, argv: [str]):

        if argv.store is None:
            sys.stdout = Logger([sys.stdout])
        else:
            sys.stdout = Logger([sys.stdout, open(argv.store, "w")])

        format_type = getattr(SupportedFormat, argv.format.upper())
        d = yaml.safe_load(sys.stdin)
        if d is None:
            d = {}
        if format_type == SupportedFormat.YAML:
            yaml.dump(d, sys.stdout)
        elif format_type == SupportedFormat.JSON:
            if argv.pretty:
                json.dump(d, sys.stdout, indent=2)
            else:
                json.dump(d, sys.stdout)
        else:
            raise Exception("Not supported format")
