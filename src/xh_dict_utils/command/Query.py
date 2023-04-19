import argparse

import yaml
from xh_dual_layer_app_engine.CommandTemplate import CommandTemplate

from xh_dict_utils import Entries


class Query(CommandTemplate):
    def __init__(self):
        super().__init__("query", "query by selector")

    def parserOp(self, parser: argparse.ArgumentParser):
        parser.add_argument("--in-format", choice=["yaml", "json"], default="yaml")
        parser.add_argument("--in-format-json", dest="in_format", action="store_const", const="json")
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
