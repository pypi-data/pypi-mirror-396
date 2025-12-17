import enum
import re
from collections.abc import Callable, Generator
from functools import wraps
from types import SimpleNamespace
from typing import NamedTuple, final, override

from more_itertools import peekable


class Type(enum.Enum):
    """A type tag for tokens."""

    INT = enum.auto()
    FLOAT = enum.auto()
    OPERATOR = enum.auto()
    IDENTIFIER = enum.auto()
    ERROR = enum.auto()
    HEAP = enum.auto()
    EOF = enum.auto()


class Token(NamedTuple):
    """Associate a "raw" token with a type tag."""

    tag: Type
    what: str

    @override
    def __str__(self):
        return f"({self.tag.name} {self.what})"


@final
class Op(SimpleNamespace):
    """The various Pratt Calc token constants.

    This exists because non-identifier tokens are always the same, for
    example, the token representing the plus operator.

    """

    eof = Token(Type.EOF, "eof")
    lparen = Token(Type.OPERATOR, "(")
    rparen = Token(Type.OPERATOR, ")")
    prt = Token(Type.OPERATOR, "print")
    at = Token(Type.OPERATOR, "@")
    plus = Token(Type.OPERATOR, "+")
    minus = Token(Type.OPERATOR, "-")
    times = Token(Type.OPERATOR, "*")
    divide = Token(Type.OPERATOR, "/")
    power = Token(Type.OPERATOR, "^")
    factorial = Token(Type.OPERATOR, "!")
    semicolon = Token(Type.OPERATOR, ";")
    assign = Token(Type.OPERATOR, "<-")
    pi = Token(Type.OPERATOR, "pi")
    sin = Token(Type.OPERATOR, "sin")
    cos = Token(Type.OPERATOR, "cos")
    tan = Token(Type.OPERATOR, "tan")
    sec = Token(Type.OPERATOR, "sec")
    csc = Token(Type.OPERATOR, "csc")
    cot = Token(Type.OPERATOR, "cot")
    quote = Token(Type.OPERATOR, "{")
    endquote = Token(Type.OPERATOR, "}")
    call = Token(Type.OPERATOR, "call")
    string = Token(Type.OPERATOR, '"')
    strcast = Token(Type.OPERATOR, "str")


@final
class Internal(SimpleNamespace):
    """Tokens used to distinguish various kinds of data that live
    inside the heap.

    User code is not allowed to produce these tokens.

    """

    code = Token(Type.HEAP, "code")
    string = Token(Type.HEAP, "string")


# See docstring for 'tokenize'.
type Stream = peekable[Token]
type tokenizer = Callable[[str], Generator[Token]]


def _stream(fn: tokenizer) -> Callable[[str], Stream]:
    """Convert the tokenizer's generator into a peekable."""

    @wraps(fn)
    def wrapper(raw_expression: str) -> Stream:
        gen = fn(raw_expression)

        return peekable(gen)

    return wrapper


@_stream
def tokenize(raw_expression: str) -> Generator[Token]:
    """Tokenize RAW_EXPRESSION.

    Integers are yielded as Python ints; everything else is yielded as
    its original string representation.

    Inspiration taken from

    https://docs.python.org/3/library/re.html

    """

    # First remove comments from source text.
    raw_expression = re.sub(r"/\*.*?\*/", "", raw_expression, flags=re.DOTALL)

    # Next, replace newlines with semicolons. This frees the
    # programmer from having to use semicolons explicitly if two
    # statements are separated by a newline. :)
    raw_expression = re.sub(r"\n+", ";", raw_expression)

    token_specification = [
        ("NUMBER", r"\d+(\.\d*)?"),
        (
            "OPERATOR",
            r"pi|sin|cos|tan|sec|csc|cot|print|call|str|<-|[-+*/!()^;{}\"]",
        ),
        ("IDENTIFIER", r"[a-zA-Z_][\w]*"),
        ("SKIP", r"[ \t]+"),
        ("ERROR", r"."),
    ]

    token_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_specification)
    pattern = re.compile(token_regex)

    for mo in re.finditer(pattern, raw_expression):
        what = mo.lastgroup
        value = mo.group()

        match what:
            case "NUMBER":
                if "." in value:
                    yield Token(Type.FLOAT, value)
                else:
                    yield Token(Type.INT, value)

            case "OPERATOR":
                yield Token(Type.OPERATOR, value)

            case "IDENTIFIER":
                yield Token(Type.IDENTIFIER, value)

            case "SKIP":
                continue

            case "ERROR":
                raise ValueError(f"Bad token: '{value}'")

            case _:
                raise ValueError(f"Fatal: unknown category '{what}:{value}'")

    yield Token(Type.EOF, "eof")
