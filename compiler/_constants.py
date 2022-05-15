# _constants.py

from typing import NamedTuple


SYMBOL_CHARS = "#+-*/=(){}"
LONG_SYMBOLS = ["++", "+="]
SEPARATORS = ";\n"

EXPR_OPS = "=+-*/()"
EXPR_OP_PRECEDENCE = {
    "(": -1,
    ")": -1,
    "=": 0,
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
}


class _InstrSet(NamedTuple):
    ADDR: str
    CONST: str


EXPR_INSTRS = {
    "=": _InstrSet("MOV", "SET"),
    "+": _InstrSet("ADD", "ADDC"),
    "-": _InstrSet("SUB", "SUBC"),
    "*": _InstrSet("MUL", "MULC"),
    "/": _InstrSet("DIV", "DIVC"),
}

SYMBOLS = list(SYMBOL_CHARS) + LONG_SYMBOLS
