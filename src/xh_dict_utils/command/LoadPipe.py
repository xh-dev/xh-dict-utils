import argparse

from xh_dual_layer_app_engine.CommandTemplate import CommandTemplate


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
