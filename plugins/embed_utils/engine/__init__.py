# flake8: noqa
__version__ = "0.1.0"

from .lexer import Lexer
from .parser import Parser
from .models import *


def compile(template: str):
    lexer = Lexer(template)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    node = parser.parse()

    embeds = []

    curr_node = node
    while curr_node is not None:

        obj_node: ObjectNode = curr_node.parent
        embeds.append(obj_node.eval())

        curr_node = curr_node.child

    return embeds


# with open("emu/example.txt", "r") as template:

#     lexer = Lexer(template.read())
#     tokens = lexer.tokenize()
#     parser = Parser(tokens)
#     node = parser.parse()

#     embeds = []

#     curr_node = node
#     while curr_node is not None:

#         obj_node: ObjectNode = curr_node.parent
#         embeds.append(obj_node.eval())

#         curr_node = curr_node.child

#     print(embeds)
