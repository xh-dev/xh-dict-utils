from enum import Enum
from pathlib import Path


class SupportedFormat(Enum):
    JSON = "json"
    YAML = "yaml"


def getKey(args):
    targetFile = Path(args.file)

    if not targetFile.exists():
        raise Exception(f'Path[{targetFile}] not exists')


def readFromFile(filePath):
    with open(filePath, "r") as f:
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                break


def traverseNode(root, nodeNotation, do=lambda parent, nodeName: (parent, nodeName)):
    if root == None:
        raise Exception("Node input is empty")

    if nodeNotation and (not nodeNotation == ""):
        levels = nodeNotation.split(".")
        nodeName = levels[-1]

        parent = root
        for x in levels[:-1]:
            if not x in parent:
                parent[x] = dict()
            parent = parent[x]

        return True, do(parent, nodeName)
    else:
        return False, None, None


