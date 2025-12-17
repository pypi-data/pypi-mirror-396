from __future__ import annotations

import enum
import math
import pathlib
from collections import UserDict
from dataclasses import dataclass
from typing import final, override

from pratt_calc.tokenizer import Internal, Op, Token, Type, tokenize


@dataclass
class Register:
    alias: str
    value: int | float

    @override
    def __str__(self):
        return f"({self.alias} {self.value})"


class Precedence(enum.IntEnum):
    """Establish the various precedence levels.

    Rather than being associated directly with a token, a given
    precedence level gets passed in as an argument whenever a given
    token is dispatched.

    For example, subtraction is dispatched using PLUS_MINUS, while
    negation is dispatched using UNARY, even though both are
    associated with the '-' token.

    """

    NONE = enum.auto()
    SEMICOLON = enum.auto()
    ASSIGNMENT = enum.auto()
    PLUS_MINUS = enum.auto()
    TIMES_DIVIDE = enum.auto()
    POWER = enum.auto()
    UNARY = enum.auto()
    FACTORIAL = enum.auto()
    IMMEDIATE = enum.auto()


class LedPrecedenceTable(UserDict[Token, Precedence]):
    """Specify precedence of LED-position tokens.

    Not all LED-position tokens are actual LEDs, since, for example,
    'eof' serves no other function than to report a precedence level
    of NONE. In most cases though, a LED-position token and a LED
    token are the same thing.

    """

    @override
    def __getitem__(self, token: Token):
        try:
            return self.data[token]
        except KeyError:
            raise ValueError(f"Led does not exist in table: '{token}'")


@final
class Evaluator:
    """An environment for evaluating expressions.

    Encapsulates a stream of Token objects as global state usable
    across recursive calls to 'expression', freeing us from having to
    return the stream (or any kind of placeholder state, for that
    matter) after each such recursive call.

    """

    led_precedence = LedPrecedenceTable(
        {
            Op.eof: Precedence.NONE,
            Op.rparen: Precedence.NONE,
            Op.plus: Precedence.PLUS_MINUS,
            Op.minus: Precedence.PLUS_MINUS,
            Op.times: Precedence.TIMES_DIVIDE,
            Op.divide: Precedence.TIMES_DIVIDE,
            Op.power: Precedence.POWER,
            Op.factorial: Precedence.FACTORIAL,
            Op.semicolon: Precedence.SEMICOLON,
            Op.assign: Precedence.ASSIGNMENT,
            Op.quote: Precedence.IMMEDIATE,
        }
    )

    def __init__(self):
        """Initialize the evaluator object.

        In particular initialize an empty token stream, to which
        EVALUATE will later append tokens comprising the expression to
        be evaluated.

        """

        # Initialize an empty token stream.
        self.stream = tokenize("")

        self.registers: list[Register] = []
        self.heap: list[Token] = []

    def evaluate(self, raw_expression: str) -> int | float:
        """Evaluate RAW_EXPRESSION.

        Note that each call to EVALUATE per object will peristently
        grow both the registers and the heap.

        """

        tokens = tokenize(raw_expression)
        self.stream.prepend(*tokens)

        return self.expression()

    def evaluate_file(self, filename: str) -> int | float:
        """Execute code in FILENAME."""

        path = pathlib.Path(filename)

        if not path.exists():
            raise FileNotFoundError(f"Fatal: '{path}' doesn't exist")

        if path.is_dir():
            raise IsADirectoryError(f"Fatal: '{path}' is a directory")

        with path.open(encoding="utf-8") as f:
            code = f.read()

            return self.evaluate(code)

    def dealias(self, alias: str) -> int:
        """Return address associated with locals alias.

        If alias doesn't exist yet, create it.

        """

        for i, register in enumerate(self.registers):
            if register.alias == alias:
                return i

        self.registers.append(Register(alias, 0))

        return len(self.registers) - 1

    def _call(self, type_addr: int) -> int | float:
        """Logic corresponding to 'call' token."""

        type_t = self.heap[type_addr]

        if type_t != Internal.code:
            raise ValueError(f"Illegal call-address: {type_addr}")

        # Get the length address.
        len_addr = type_addr + 1
        code_len = int(self.heap[len_addr].what)

        # Get the code address.
        code_addr = len_addr + 1
        code = self.heap[code_addr : code_addr + code_len]
        self.stream.prepend(*code)

        return self.expression(Precedence.NONE)

    def _quote(self, ignore: bool = False) -> int | float:
        """Logic corresponding to 'quote' token."""

        # Note that this case doesn't call
        # 'expression': it flatly consumes the next
        # series of tokens until '}' is seen.
        start = len(self.heap)
        code_expr: list[Token] = []

        quote_stack = 1

        while True:
            t = next(self.stream)

            if t == Op.quote:
                quote_stack += 1
                code_expr.append(t)
            elif t == Op.endquote:
                quote_stack -= 1

                if quote_stack == 0:
                    break
                else:
                    code_expr.append(t)
            else:
                code_expr.append(t)

        if ignore:
            return self.expression()
        else:
            self.heap.append(Internal.code)
            self.heap.append(Token(Type.INT, str(len(code_expr))))
            self.heap.extend(code_expr)

            return start

    def expression(self, level: int = Precedence.NONE) -> int | float:
        """Pratt-parse an arithmetic expression, evaluating it."""

        # NUD
        current = next(self.stream)

        match current.tag:
            case Type.INT:
                acc = int(current.what)

            case Type.FLOAT:
                acc = float(current.what)

            case Type.IDENTIFIER:
                rindex = self.dealias(current.what)

                # We cheat a little here: if the next token is '<-',
                # this identifier token is in a left-hand-side
                # position of an assignment operation, and so the
                # token should evaluate to the register index, just as
                # it did originally.
                if (t := self.stream.peek()) == Op.assign:
                    acc = rindex
                else:
                    acc = self.registers[rindex].value

            case Type.EOF:
                acc = 0

            case Type.OPERATOR:
                match current:
                    case Op.pi:
                        acc = math.pi

                    case Op.sin:
                        acc = math.sin(self.expression(Precedence.UNARY))

                    case Op.cos:
                        acc = math.cos(self.expression(Precedence.UNARY))

                    case Op.tan:
                        acc = math.tan(self.expression(Precedence.UNARY))

                    case Op.sec:
                        acc = 1 / math.cos(self.expression(Precedence.UNARY))

                    case Op.csc:
                        acc = 1 / math.sin(self.expression(Precedence.UNARY))

                    case Op.cot:
                        acc = 1 / math.tan(self.expression(Precedence.UNARY))

                    case Op.minus:
                        acc = -self.expression(Precedence.UNARY)

                    case Op.lparen:
                        acc = self.expression(Precedence.NONE)

                        # We don't drive parsing/evaluation with right-paren,
                        # so we skip it as we read it.
                        assert next(self.stream) == Op.rparen

                    case Op.prt:
                        type_addr = int(self.expression(Precedence.UNARY))
                        type_t = self.heap[type_addr]

                        if type_t != Internal.string:
                            raise ValueError(f"Illegal string-address: {type_addr}")

                        len_addr = type_addr + 1
                        string_len = int(self.heap[len_addr].what)

                        # Get the address of the string itself.
                        string_addr = len_addr + 1
                        string = self.heap[string_addr : string_addr + string_len]

                        print(" ".join([s.what for s in string]))

                        acc = self.expression(Precedence.NONE)

                    case Op.quote:
                        acc = self._quote()

                    case Op.call:
                        type_addr = int(self.expression(Precedence.UNARY))
                        acc = self._call(type_addr)

                    case Op.semicolon:
                        # As a nud, ';' is a no-op. This lets users
                        # input empty "statements" like ';;'. It also
                        # lets a preprocessing step inject semicolons
                        # in place of newlines.
                        acc = self.expression(Precedence.NONE)

                    case Op.string:
                        start = len(self.heap)
                        string_expr: list[Token] = []

                        while (t := next(self.stream)) != Op.string:
                            string_expr.append(t)

                        self.heap.append(Internal.string)
                        self.heap.append(Token(Type.INT, str(len(string_expr))))
                        self.heap.extend(string_expr)

                        acc = start

                    case Op.strcast:
                        value = self.expression(Precedence.UNARY)
                        acc = len(self.heap)

                        self.heap.append(Internal.string)
                        self.heap.append(Token(Type.INT, "1"))
                        self.heap.append(Token(Type.INT, f"{value}"))

                    case _ as nonexistent:
                        raise ValueError(f"Invalid nud: '{nonexistent}'")

            case _:
                raise ValueError(f"Invalid token: '{current}'")

        while level < self.led_precedence[self.stream.peek()]:
            current = next(self.stream)

            # LED
            match current:
                case Op.plus:
                    acc += self.expression(Precedence.PLUS_MINUS)

                case Op.minus:
                    acc -= self.expression(Precedence.PLUS_MINUS)

                case Op.times:
                    acc *= self.expression(Precedence.TIMES_DIVIDE)

                case Op.divide:
                    acc /= self.expression(Precedence.TIMES_DIVIDE)

                case Op.power:
                    # Enforce right-association by subtracting 1 from
                    # the precedence argument.
                    acc = math.pow(acc, self.expression(Precedence.POWER - 1))

                case Op.factorial:
                    # Compute factorial by hand.
                    #
                    # If ACC is a float, truncate it first to an int.
                    prod = 1

                    acc = int(acc)

                    for j in range(1, acc + 1):
                        prod *= j

                        acc = prod

                case Op.semicolon:
                    # Discard the left-hand side, keeping only the
                    # right-hand side. This will hopefully be useful
                    # for side-effects later.
                    acc = self.expression(Precedence.SEMICOLON)

                case Op.assign:
                    # Assignment is right-associative.
                    right_hand_side = self.expression(Precedence.ASSIGNMENT - 1)

                    # Truncate 'acc' so that we can use it as an index
                    # into our registers.
                    self.registers[int(acc)].value = right_hand_side

                    # Set the current result to 'right_hand_side',
                    # like with Lisp's 'setq'.
                    acc = right_hand_side

                case Op.quote:
                    # Conditional execution.
                    flag = acc

                    if flag != 0:
                        type_addr = int(self._quote())
                        acc = self._call(type_addr)

                    else:
                        acc = self._quote(ignore=True)

                case _ as token:
                    raise ValueError(f"Invalid led: {token}")

        return acc
