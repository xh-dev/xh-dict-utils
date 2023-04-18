import argparse
import os
import sys

import yaml
from xh_dual_layer_app_engine.CommandTemplate import CommandTemplate

from xh_dict_utils import Entries


class UpsertNode(CommandTemplate):
    def __init__(self):
        super().__init__("upsert-node", "update or insert to a node")

    def parserOp(self, parser: argparse.ArgumentParser):
        parser.add_argument("--selector", type=str)
        parser.add_argument("--dict-from-file", type=str)
        parser.add_argument("--dict-from-pipe", action="store_true", default=False)

        # parser.add_argument("--key", type=str)

        parser.add_argument("--node-value", type=str)
        parser.add_argument("--node-value-file", type=str)

        parser.add_argument("--node-value-type", type=str, default="str",
                            choices=["str", "int", "number", "object"])
        parser.add_argument("--node-value-type-str", dest="node_value_type", action="store_const", const="str")
        parser.add_argument("--node-value-type-int", dest="node_value_type", action="store_const", const="int")
        parser.add_argument("--node-value-type-number", dest="node_value_type", action="store_const",
                            const="number")
        parser.add_argument("--node-value-type-object", dest="node_value_type", action="store_const",
                            const="object")

    def handleOp(self, argv: [str]):
        selector = argv.selector

        dict_from_pipe = argv.dict_from_pipe
        dict_from_file = argv.dict_from_file
        node_value_file = argv.node_value_file
        node_value = argv.node_value
        node_value_type = argv.node_value_type
        # key = argv.key

        node_value_from_pipe = True if node_value is None and node_value_file is None else False

        def validate():
            if node_value_from_pipe and dict_from_pipe:
                raise Exception("Cannot read `dictionary` and `node-value` both from pipe")
            if not node_value_from_pipe:
                node_value_file = argv.node_value_file
                node_value = argv.node_value
                if node_value_file is not None and node_value is not None:
                    raise Exception(
                        f"node-value-file[{node_value_file}] and node-value[{node_value}] is mutually exclusive")
                if node_value_file is not None:
                    if not os.path.exists(node_value_file):
                        raise Exception(f"[{node_value_file}] not exists")
                    if not os.path.isfile(node_value_file):
                        raise Exception(f"[{node_value_file}] not a file")
            if not dict_from_pipe:
                if not os.path.exists(dict_from_file):
                    raise Exception(f"[{dict_from_file}] not exists")
                if not os.path.isfile(dict_from_file):
                    raise Exception(f"[{dict_from_file}] not a file")

        validate()

        d = yaml.safe_load(sys.stdin.read() if dict_from_pipe else open(dict_from_file).read())
        entries = Entries.from_dict(d).match_notation(selector)

        def load():
            if node_value is not None:
                data = node_value
            elif node_value_file:
                data = open(node_value_file, "r").read()
            elif node_value_from_pipe:
                data = sys.stdin.read()
            else:
                raise Exception("Not supported node-value type")

            if node_value_type == "str":
                return data
            elif node_value_type == "int":
                return int(data)
            elif node_value_type == "number":
                return float(data)
            elif node_value_type == "object":
                return yaml.safe_load(data)
            else:
                raise Exception("Not supported node-value type")

        node_value_content = load()
        if entries.unique_result():
            head = entries.head()
            parent = head.parent
            key, _ = head.selector.key_and_parent()
            entries.head_and_tail()
            if type(parent.value) is dict:
                # if key is None:
                #     raise Exception("key is empty")
                parent.value.update({key: node_value_content})
            elif type(parent.value) is list:
                parent.value.append(node_value_content)
            else:
                key, _ = head.selector.key_and_parent()
                parent.value.update({key: node_value_content})
        elif entries.no_result():
            raise Exception("no record found")
        else:
            raise Exception("multiple record result")

        yaml.dump(d, sys.stdout)
