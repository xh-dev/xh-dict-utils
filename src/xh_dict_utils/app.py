import argparse
import json
import os
import sys

import yaml

from xh_dict_utils.ExtractFromFile import SupportedFormat
from xh_dict_utils.Layer1AppEngine import AppEngine
from xh_dict_utils.command.ToArray import *
from xh_dict_utils.command.CommandTemplate import *
from xh_dict_utils.dict_utils import Entries, Selector


def main():
    PROGRAM_NAME = "yaml-json-modification"
    DESCRIPTION = "A simple program modify yaml or json file"
    appEngine = AppEngine(
        program_name=PROGRAM_NAME,
        description=DESCRIPTION,
    )

    class LoadPipe(CommandTemplate):
        def __init__(self):
            super().__init__("load-pipe", "load from pipe")

        def parserOp(self, parser: argparse.ArgumentParser):
            parser.add_argument("--format", choices=["json", "yaml"], default="yaml")

        def handleOp(self, argv: [str]):
            format_type = getattr(SupportedFormat, argv.format.upper())
            if format_type == SupportedFormat.YAML:
                d = yaml.safe_load(sys.stdin.read())
            elif format_type == SupportedFormat.JSON:
                d = json.loads(sys.stdin.read())
            else:
                raise Exception("Not supported format")
            yaml.dump(d, sys.stdout)

    appEngine.regSubCommandWithTemplate(LoadPipe())

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

    appEngine.regSubCommandWithTemplate(LoadFile())

    class UpsertNode(CommandTemplate):
        def __init__(self):
            super().__init__("upsert-node", "update or insert to a node")

        def parserOp(self, parser: argparse.ArgumentParser):
            parser.add_argument("--selector", type=str)
            parser.add_argument("--dict-from-file", type=str)
            parser.add_argument("--dict-from-pipe", action="store_true", default=False)

            parser.add_argument("--key", type=str)

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
            key = argv.key

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
                if type(head.value) is dict or type(head.value) is list:
                    head.value = node_value_content
                # if type(head.value) is dict:
                #     if key is None:
                #         raise Exception("key is empty")
                #     head.value.update({key: node_value_content})
                # elif type(head.value) is list:
                #     head.value = node_value_content
                else:
                    key, _ = head.selector.key_and_parent()
                    head.parent.value.update({key: node_value_content})
            elif entries.no_result():
                raise Exception("no record found")
            else:
                raise Exception("multiple record result")

            yaml.dump(d, sys.stdout)

    appEngine.regSubCommandWithTemplate(UpsertNode())

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

    appEngine.regSubCommandWithTemplate(RemoveNode())

    class Query(CommandTemplate):
        def __init__(self):
            super().__init__("query", "query by selector")

        def parserOp(self, parser: argparse.ArgumentParser):
            parser.add_argument("--selector", type=str)
            parser.add_argument("--output", type=str, default="{selector} -> {value}")
            parser.add_argument("--exact", dest="notation_type", action="store_const", const="exact")
            parser.add_argument("--regex", dest="notation_type", action="store_const", const="regex")
            parser.set_defaults(notation_type="notation")
            parser.set_defaults(exact=False)

        def handleOp(self, argv: [str]):
            selector = argv.selector
            if argv.notation_type == "exact":
                findings = Entries.from_dict(yaml.safe_load(sys.stdin)).match_exact(selector)
            elif argv.notation_type == "regex":
                findings = Entries.from_dict(yaml.safe_load(sys.stdin)).match_regex(selector)
            if argv.notation_type == "notation":
                findings = Entries.from_dict(yaml.safe_load(sys.stdin)).match_notation(selector)

            for finding in findings.asGenerator():
                print(argv.output.format_map(
                    {"selector": finding.selector.selector_str, "value": finding.value, "context": finding}))

    appEngine.regSubCommandWithTemplate(Query())

    appEngine.regSubCommandWithTemplate(ToArray())

    class Output(CommandTemplate):
        def __init__(self):
            super().__init__("output", "output as json")

        def parserOp(self, parser: argparse.ArgumentParser):
            parser.add_argument("--store", type=str, default=None)
            parser.add_argument("--format", choices=["json", "yaml"])
            parser.add_argument("--pretty", action="store_true", default=False)

        def handleOp(self, argv: [str]):
            class Logger(object):
                def __init__(self, channel: list):
                    self.channels = channel

                def write(self, message):
                    for channel in self.channels:
                        channel.write(message)

                def flush(self):
                    # this flush method is needed for python 3 compatibility.
                    # this handles the flush command by doing nothing.
                    # you might want to specify some extra behavior here.
                    pass

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

    appEngine.regSubCommandWithTemplate(Output())

    appEngine.process(sys.argv)
