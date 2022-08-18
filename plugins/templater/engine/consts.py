import string


ALL_CHARACTERS = string.printable.strip()

LETTERS = string.ascii_letters
WHITESPACE = string.whitespace

LIST_KW = [
    "fields",
]

CLASS_KW = [
    "footer",
    "field",
    "author",
    "image",
    "thumbnail",
    "embed",
]


ATTR_KW = [
    "url",
    "icon_url",
    "description",
    "color",
    "name",
    "value",
    "title",
]


VALID_KW = LIST_KW + CLASS_KW + ATTR_KW
