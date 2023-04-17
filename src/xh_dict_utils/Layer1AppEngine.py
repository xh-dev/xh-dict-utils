import argparse
from abc import ABC, abstractmethod
from typing import Callable, List


class CommandTemplate(ABC):
    def __init__(self, name: str, help: str):
        self.name = name
        self.help = help

    @abstractmethod
    def parserOp(self, parser: argparse.ArgumentParser):
        pass

    @abstractmethod
    def handleOp(self, argv: [str]):
        pass


class AppEngine:
    def __parser_setup(self) -> argparse.ArgumentParser:
        return argparse.ArgumentParser(
            prog=self.program_name,
            description=self.description,
            # epilog='Text at the bottom of help'
        )

    def __sub_parser_setup(self: "AppEngine") -> argparse.ArgumentParser:
        return self.root_parser.add_subparsers(title='subcommands', description='commands', help='commands')

    def __init__(self, program_name: str, description: str,
                 parser_setup: Callable[["AppEngine"], argparse.ArgumentParser] = __parser_setup,
                 sub_parser_setup: Callable[
                     ["AppEngine", argparse.ArgumentParser], argparse.ArgumentParser] = __sub_parser_setup
                 ):
        self.program_name = program_name
        self.description = description
        self.root_parser = parser_setup(self)
        self.subparsers = sub_parser_setup(self)
        self.subCommands = dict()
        self.handlers = dict()

    def regSubCommand(self, key: str, help: str, parserOp: Callable[[argparse.ArgumentParser], None],
                      handle: Callable[[List[str]], None]):
        if key not in self.subCommands:
            parser = self.subparsers.add_parser(key, help=help)
            parserOp(parser)
            self.subCommands.update({key: parser})

            def handling(args):
                # parsed_args = root_parser.parse_args(args)
                parsed_args = parser.parse_args(args)
                handle(parsed_args)

            self.handlers.update({key: handling})
        return

    def process(self, allArgs: [str]):
        if len(allArgs) < 2:
            self.root_parser.print_help()
            exit(1)

        key = allArgs[1]
        if key not in self.subCommands:
            raise Exception(f"command[{key}] not valid")

        self.handlers[key](allArgs[2:])

    def regSubCommandWithTemplate(self, param: CommandTemplate):
        self.regSubCommand(param.name, param.help, param.parserOp, param.handleOp)
