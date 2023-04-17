import re
from dataclasses import dataclass
from enum import Enum
from typing import Generator, Callable, Union, Tuple


class EntryType(Enum):
    DICT = 0
    LIST = 1
    LIST_ITEM = 2
    VALUE = 3


class Selector:
    __ROOT_SELECTOR: "Selector" = None
    selector_str: str

    def __init__(self, selector_str: str):
        self.selector_str = selector_str

    def is_root(self):
        return self.selector_str == ""

    def is_not_root(self):
        return not self.is_root()

    def is_array(self):
        compiled = re.compile("^.*\\.\\[(\\d+|\\*)]$")
        return compiled.match(self.selector_str) is not None

    def is_array_group(self):
        compiled = re.compile("^.*\\.\\[\\*]$")
        return compiled.match(self.selector_str) is not None

    def is_array_item(self):
        compiled = re.compile("^.*\\.\\[\\d+]$")
        return compiled.match(self.selector_str) is not None

    def get_array_index(self):
        if self.is_array_item():
            return int(self.selector_str.split(".")[-1][1:-1])
        else:
            raise Exception("Not an array item")

    def is_object_or_value(self):
        return not self.is_array()

    @staticmethod
    def root():
        if Selector.__ROOT_SELECTOR is None:
            Selector.__ROOT_SELECTOR = Selector("")
        return Selector.__ROOT_SELECTOR

    @staticmethod
    def from_notation(notation_str: str) -> 'Selector':
        return Selector(notation_str)

    def depth(self):
        return len(self.dot_chain())

    def object_or_value(self, key: str):
        return Selector(f"{key}") if self.is_root() else Selector(f"{self.selector_str}.{key}")

    def list_item(self, key: int):
        ends_with = ".[*]"
        offset = len(ends_with) * -1
        if self.selector_str.endswith(ends_with):
            return Selector(f"[{key}]") if self.is_root() else Selector(f"{self.selector_str[:offset]}.[{key}]")
        else:
            return Selector(f"[{key}]") if self.is_root() else Selector(f"{self.selector_str}.[{key}]")

    # def list_group(self):
    #     return Selector(f"[*]") if self.is_root() else Selector(f"{self.selector_str}.[*]")

    def list_group(self, index: int):
        return Selector(f"{index}.[*]") if self.is_root() else Selector(f"{self.selector_str}.{index}.[*]")

    def pop(self):
        return self.key_and_parent()[1]

    def dot_chain(self) -> [str]:
        return [i for i in self.selector_str.split(".") if i != "[*]"]
    def key_and_parent(self):
        splited = self.dot_chain()
        if self.is_root():
            return Selector.root(), None
        elif len(splited) == 1:
            return splited[0], Selector.root()
        else:
            return splited[-1], Selector(".".join(splited[:-1]))


@dataclass
class Entry:
    selector: Selector
    value: any
    parent: Union["Entry", None]

    def get_entry_type(self):
        if type(self.value) is dict:
            return EntryType.DICT
        elif type(self.value) is list:
            return EntryType.LIST
        else:
            return EntryType.VALUE

    def get_selector(self):
        return self.selector.selector_str

    def is_not_root(self):
        return self.selector.is_not_root()

    def is_root(self):
        return self.selector.is_root()

    def get_dict(self, key: str):
        return Entry(self.selector.object_or_value(key), {}, self)

    def get_list(self, key: int):
        return Entry(self.selector.list_item(key), [], self)

    def get_any_list(self):
        return Entry(self.selector.list_group(), [], self)

    def get_value(self, key: str, value: any):
        return Entry(self.selector.object_or_value(key), value, self)

    def match(self, matching: Callable[["Entry"], bool]) -> bool:
        return matching(self)

    def match_notation(self, selector: str):
        if selector == "":
            return self.is_root()
        notation_reg = selector.replace("[*]", "\\[[\\d|\\*]+\\]")
        return self.regex_selector(notation_reg)

    def exact_selector(self, selector: str):
        return self.match(lambda entry: entry.selector.selector_str == selector)

    def regex_selector(self, selector: str):
        compiled_selector = re.compile(selector)
        return self.match(lambda select: compiled_selector.match(select.get_selector()) is not None)

    def getIndex(self):
        return self.selector.get_array_index()

    def isList(self):
        return self.get_entry_type() == EntryType.LIST

    def isDict(self):
        return self.get_entry_type() == EntryType.DICT

    def isValue(self):
        return self.get_entry_type() == EntryType.VALUE

    def __str__(self):
        if self.is_root():
            return f"Root({self.value})"
        else:
            return f"Entry({self.get_selector()}, {self.value})"

    def __repr__(self):
        return self.__str__()


class Entries:
    entries: [Entry]

    def __init__(self, entries: [Entry]):
        self.entries = entries

    def match_exact(self, selector: str) -> "Entries":
        return Entries([t for t in self.entries if t.exact_selector(selector)])

    def match_regex(self, selector: str) -> "Entries":
        return Entries([t for t in self.entries if t.regex_selector(selector)])

    def match_notation(self, selector: str) -> "Entries":
        return Entries([t for t in self.entries if t.match_notation(selector)])

    def asGenerator(self) -> Generator[Entry, None, None]:
        yield from self.entries

    def asList(self) -> Generator[Entry, None, None]:
        yield from self.entries

    def size(self):
        return len(self.entries)

    def head_and_tail(self) -> Tuple[Entry, "Entries"]:
        head = self.entries[0] if len(self.entries) > 0 else None
        tail = Entries(self.entries[1:] if len(self.entries) > 1 else [])
        return head, tail

    def head(self):
        head, _ = self.head_and_tail()
        return head

    def tail(self):
        _, tail = self.head_and_tail()
        return tail

    def unique_result(self):
        return self.size() == 1

    def no_result(self):
        return self.size() == 0

    def multi_result(self):
        return self.size() > 1

    @staticmethod
    def from_dict(someNode: any) -> "Entries":
        if someNode is None:
            raise Exception(f"Input node is None")

        def innerFlatten(innerSomeNode: any, parent: Entry = None) \
                -> Generator[Entry, None, None]:
            if type(innerSomeNode) is dict:
                yield parent
                for key, value in innerSomeNode.items():
                    if type(value) is list:
                        entry = Entry(parent.selector.list_group(key), value, parent)
                        yield from innerFlatten(value, entry)
                    else:
                        entry = Entry(parent.selector.object_or_value(key), value, parent)
                        yield from innerFlatten(value, entry)
            elif type(innerSomeNode) is list:
                yield parent
                for index, value in enumerate(innerSomeNode):
                    entry = Entry(parent.selector.list_item(index), value, parent)
                    yield from innerFlatten(value, entry)
            else:
                yield parent

        return Entries(list(innerFlatten(someNode, Entry(Selector.root(), someNode, None))))

    @staticmethod
    def select_by_notation(dictionary: dict, notation: str) -> "Entries":
        return Entries.from_dict(dictionary).match_notation(notation)

    def __str__(self):
        return "\n".join([str(entry) for entry in self.entries])

    def __repr__(self):
        return self.__str__()
