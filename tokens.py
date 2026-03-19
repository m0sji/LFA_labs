"""Token definitions for the mini language lexer.

This project requires a file named ``token.py``. To avoid breaking Python's
standard library imports (which also use a module named ``token``), this file
includes stdlib-compatible token constants first, then adds lab-specific types.
"""

from __future__ import annotations

# ---- Begin stdlib-compatible `token` symbols ----
__all__ = ["tok_name", "ISTERMINAL", "ISNONTERMINAL", "ISEOF", "EXACT_TOKEN_TYPES"]

ENDMARKER = 0
NAME = 1
NUMBER = 2
STRING = 3
NEWLINE = 4
INDENT = 5
DEDENT = 6
LPAR = 7
RPAR = 8
LSQB = 9
RSQB = 10
COLON = 11
COMMA = 12
SEMI = 13
PLUS = 14
MINUS = 15
STAR = 16
SLASH = 17
VBAR = 18
AMPER = 19
LESS = 20
GREATER = 21
EQUAL = 22
DOT = 23
PERCENT = 24
LBRACE = 25
RBRACE = 26
EQEQUAL = 27
NOTEQUAL = 28
LESSEQUAL = 29
GREATEREQUAL = 30
TILDE = 31
CIRCUMFLEX = 32
LEFTSHIFT = 33
RIGHTSHIFT = 34
DOUBLESTAR = 35
PLUSEQUAL = 36
MINEQUAL = 37
STAREQUAL = 38
SLASHEQUAL = 39
PERCENTEQUAL = 40
AMPEREQUAL = 41
VBAREQUAL = 42
CIRCUMFLEXEQUAL = 43
LEFTSHIFTEQUAL = 44
RIGHTSHIFTEQUAL = 45
DOUBLESTAREQUAL = 46
DOUBLESLASH = 47
DOUBLESLASHEQUAL = 48
AT = 49
ATEQUAL = 50
RARROW = 51
ELLIPSIS = 52
COLONEQUAL = 53
EXCLAMATION = 54
OP = 55
TYPE_IGNORE = 56
TYPE_COMMENT = 57
SOFT_KEYWORD = 58
FSTRING_START = 59
FSTRING_MIDDLE = 60
FSTRING_END = 61
TSTRING_START = 62
TSTRING_MIDDLE = 63
TSTRING_END = 64
COMMENT = 65
NL = 66
ERRORTOKEN = 67
ENCODING = 68
N_TOKENS = 69
NT_OFFSET = 256

tok_name = {
    value: name
    for name, value in globals().items()
    if isinstance(value, int) and not name.startswith("_")
}
__all__.extend(tok_name.values())

EXACT_TOKEN_TYPES = {
    "!": EXCLAMATION,
    "!=": NOTEQUAL,
    "%": PERCENT,
    "%=": PERCENTEQUAL,
    "&": AMPER,
    "&=": AMPEREQUAL,
    "(": LPAR,
    ")": RPAR,
    "*": STAR,
    "**": DOUBLESTAR,
    "**=": DOUBLESTAREQUAL,
    "*=": STAREQUAL,
    "+": PLUS,
    "+=": PLUSEQUAL,
    ",": COMMA,
    "-": MINUS,
    "-=": MINEQUAL,
    "->": RARROW,
    ".": DOT,
    "...": ELLIPSIS,
    "/": SLASH,
    "//": DOUBLESLASH,
    "//=": DOUBLESLASHEQUAL,
    "/=": SLASHEQUAL,
    ":": COLON,
    ":=": COLONEQUAL,
    ";": SEMI,
    "<": LESS,
    "<<": LEFTSHIFT,
    "<<=": LEFTSHIFTEQUAL,
    "<=": LESSEQUAL,
    "=": EQUAL,
    "==": EQEQUAL,
    ">": GREATER,
    ">=": GREATEREQUAL,
    ">>": RIGHTSHIFT,
    ">>=": RIGHTSHIFTEQUAL,
    "@": AT,
    "@=": ATEQUAL,
    "[": LSQB,
    "]": RSQB,
    "^": CIRCUMFLEX,
    "^=": CIRCUMFLEXEQUAL,
    "{": LBRACE,
    "|": VBAR,
    "|=": VBAREQUAL,
    "}": RBRACE,
    "~": TILDE,
}


def ISTERMINAL(x: int) -> bool:
    """Check if x is a terminal token id."""
    return x < NT_OFFSET


def ISNONTERMINAL(x: int) -> bool:
    """Check if x is a non-terminal token id."""
    return x >= NT_OFFSET


def ISEOF(x: int) -> bool:
    """Check if x is the end-of-file token id."""
    return x == ENDMARKER


# ---- End stdlib-compatible `token` symbols ----

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """All token categories recognized by the lab lexer."""

    # Literals and identifiers
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Trigonometric functions
    SIN = auto()
    COS = auto()
    TAN = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    LET = auto()

    # Boolean literals
    TRUE = auto()
    FALSE = auto()

    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()

    # Comparison and assignment
    EQ_EQ = auto()
    BANG_EQ = auto()
    LT = auto()
    GT = auto()
    LT_EQ = auto()
    GT_EQ = auto()
    ASSIGN = auto()

    # Grouping symbols
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()

    EOF = auto()


@dataclass(slots=True)
class Token:
    """Represents one token emitted by the lexer."""

    type: TokenType
    value: object
    line: int
    column: int


__all__.extend(["TokenType", "Token"])
