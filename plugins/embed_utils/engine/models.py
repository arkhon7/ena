from __future__ import annotations
from dataclasses import dataclass

import typing as t


T = t.TypeVar("T")


@dataclass
class Token(t.Generic[T]):
    type: str
    value: t.Optional[T] = None

    def __repr__(self) -> str:

        if self.value:
            return "Token(type='{}', value='{}')".format(self.type, self.value)

        return "Token(type='{}')".format(self.type)


@dataclass
class Node:
    parent: t.Any
    child: t.Optional[Node] = None


@dataclass
class AttributeNode:
    """
    named attribute
    """

    name: str
    value: t.Any

    def eval(self):
        return {self.name: self.value}


@dataclass
class ListNode:
    name: str
    value: t.List[PartialObjectNode]

    def eval(self):

        return {self.name: [v.eval() for v in self.value]}


@dataclass
class ObjectNode:
    name: str
    value: t.List[t.Union[ObjectNode, ListNode, AttributeNode]]

    def eval(self):
        output = {}

        for v in self.value:
            try:
                output[self.name].update(v.eval())

            except KeyError:
                output[self.name] = {}
                output[self.name].update(v.eval())

        return output


@dataclass
class PartialObjectNode:
    value: t.List[t.Union[ObjectNode, ListNode, AttributeNode]]

    def eval(self):
        output = {}

        for v in self.value:

            output.update(v.eval())

        return output
