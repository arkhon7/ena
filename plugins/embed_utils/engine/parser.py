from .models import (
    Token,
    Node,
    AttributeNode,
    ListNode,
    ObjectNode,
    PartialObjectNode,
)
from .consts import CLASS_KW, LIST_KW

import typing as t


class Parser:
    def __init__(self, tokens) -> None:
        self._curr_token: t.Optional[Token[str]] = None
        self._tokens: t.List[Token[str]] = tokens
        self._iter_tokens = iter(tokens)

    def advance(self):
        try:
            self._curr_token = next(self._iter_tokens)

        except StopIteration:
            self._curr_token = None

    def parse(self):

        node = self.node()

        return node

    def node(self):

        node = None
        self.advance()

        while self._curr_token is not None:
            node = Node(parent=self.new_node(), child=self.node())

            self.advance()

        return node

    def new_node(self):

        while self._curr_token is not None:

            if self._curr_token.type == "ATTR":
                return self.attr_node()

            elif self._curr_token.type == "OBJ_START":
                if self._curr_token.value in CLASS_KW:
                    return self.obj_node()

                elif self._curr_token.value in LIST_KW:
                    return self.list_node()

            elif self._curr_token.type == "PARTIAL_OBJ_START":
                return self.partial_obj_node()

            self.advance()

    def attr_node(self):
        last_tok = self._curr_token
        self.advance()

        return AttributeNode(name=last_tok.value, value=self._curr_token.value)

    def obj_node(self):
        last_tok = self._curr_token
        self.advance()
        props = []
        while (
            self._curr_token is not None
            and self._curr_token.type != "OBJ_END"
            and self._curr_token.value != last_tok.value
        ):
            props.append(self.new_node())

            self.advance()

        return ObjectNode(name=last_tok.value, value=props)

    def list_node(self):
        last_tok = self._curr_token
        self.advance()
        props = []

        while (
            self._curr_token is not None
            and self._curr_token.type != "OBJ_END"
            and self._curr_token.value != last_tok.value
        ):

            props.append(self.partial_obj_node())
            self.advance()

        return ListNode(name=last_tok.value, value=props)

    def partial_obj_node(self):
        last_tok = self._curr_token
        props = []
        self.advance()
        while (
            self._curr_token is not None
            and self._curr_token.type != "PARTIAL_OBJ_END"
            and self._curr_token.value != last_tok.value
        ):
            props.append(self.new_node())
            self.advance()

        return PartialObjectNode(value=props)
