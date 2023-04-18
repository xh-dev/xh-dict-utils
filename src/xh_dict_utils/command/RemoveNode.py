import argparse
import sys

import yaml
from xh_dual_layer_app_engine.CommandTemplate import CommandTemplate

from xh_dict_utils.dict_utils import Selector, Entries


class RemoveNode(CommandTemplate):
    def __init__(self):
        super().__init__("remove-node", "remove a node")

    def parserOp(self, parser: argparse.ArgumentParser):
        parser.add_argument("--selector", type=str)

    def handleOp(self, argv: [str]):
        selector = argv.selector
        if Selector.from_notation(selector).is_array_group():
            is_array_group = True
        else:
            is_array_group = False

        d = yaml.safe_load(sys.stdin.read())

        if is_array_group:
            entries = Entries.from_dict(d).match_exact(selector)
        else:
            entries = Entries.from_dict(d).match_notation(selector)

        for entry in entries.asGenerator():
            if entry.is_root():
                raise Exception("Can not remove root element")

        for entry in entries.asGenerator():
            parent = entry.parent
            if type(parent.value) is dict:
                key, _ = entry.selector.key_and_parent()
                del parent.value[key]
            elif type(parent.value) is list and entry.selector.is_array_item():
                index = entry.selector.get_array_index()
                del parent.value[index]
            else:
                raise Exception("Not support")
        print(d)
