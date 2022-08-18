from .models import (
    Token,
    Node,
    ObjectNode,
    PartialObjectNode,
    ListNode,
    AttributeNode,
)
from .consts import (
    CLASS_KW,
    LIST_KW,
    WHITESPACE,
    VALID_KW,
    ALL_CHARACTERS,
)


import typing as t


OBJ_START_SYMBOL = "%"
ATTR_SYMBOL = "+"
OBJ_END_SYMBOL = "$"


SYMBOLS = [OBJ_START_SYMBOL, ATTR_SYMBOL, OBJ_END_SYMBOL]


class Lexer:
    def __init__(self, text) -> None:
        self._curr_value = None
        self._text: str = text
        self._iter_text: t.Iterator[str] = iter(self._text.strip())

    def advance(self):

        try:

            self._curr_value = next(self._iter_text)

        except StopIteration:
            self._curr_value = None

    def get_keyword(self):

        keyword = ""

        while (
            self._curr_value is not None and self._curr_value not in WHITESPACE
        ):

            keyword += self._curr_value
            self.advance()

        if keyword in VALID_KW:
            return keyword

        raise Exception("invalid keyword '{}'".format(keyword))

    def tokenize(self):

        self.advance()

        tokens = []

        while self._curr_value is not None:

            if self._curr_value == ATTR_SYMBOL:
                self.advance()
                tokens.append(Token(type="ATTR", value=self.get_keyword()))
                self.advance()

            elif self._curr_value == OBJ_START_SYMBOL:
                self.advance()

                if self._curr_value in WHITESPACE:
                    tokens.append(Token(type="PARTIAL_OBJ_START"))
                    self.advance()

                else:
                    tokens.append(
                        Token(type="OBJ_START", value=self.get_keyword())
                    )
                    self.advance()

            elif self._curr_value == OBJ_END_SYMBOL:
                self.advance()

                if self._curr_value is None or self._curr_value in WHITESPACE:
                    tokens.append(Token(type="PARTIAL_OBJ_END"))
                    self.advance()

                else:
                    tokens.append(
                        Token(type="OBJ_END", value=self.get_keyword())
                    )
                    self.advance()

            elif self._curr_value in ALL_CHARACTERS:

                sentence = ""
                while (
                    self._curr_value is not None
                    and self._curr_value not in SYMBOLS
                ):

                    if self._curr_value == "\\":
                        self.advance()
                        sentence += self._curr_value
                        self.advance()
                    else:
                        sentence += self._curr_value
                        self.advance()

                tokens.append(Token(type="SENTENCE", value=sentence.strip()))
            else:
                self.advance()

        return tokens


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
