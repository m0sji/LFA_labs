"""Token type definitions for the lab language."""

from enum import Enum, auto


class TokenType(Enum):
    """Enumeration of all token kinds recognized by the lexer."""

    IDENTIFIER = auto()
    INTEGER = auto()

    ASSIGN = auto()  # =
    PLUS = auto()  # +
    MINUS = auto()  # -
    MUL = auto()  # *
    DIV = auto()  # /

    LPAREN = auto()  # (
    RPAREN = auto()  # )
    SEMICOLON = auto()  # ;

    EOF = auto()
