import argparse
from abc import ABC, abstractmethod


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

