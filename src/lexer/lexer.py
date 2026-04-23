"""Regex-based lexer for a small assignment/expression language."""

from __future__ import annotations

import re

from lexer.token import Token
from lexer.token_type import TokenType


class LexerError(ValueError):
    """Raised when the lexer encounters an invalid character."""


class Lexer:
    """Converts source text into a list of `Token` objects."""

    # Ordered token patterns. Order matters when patterns can overlap.
    TOKEN_PATTERNS: list[tuple[str, str]] = [
        ("WHITESPACE", r"[ \t\r\n\f\v]+"),
        ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("INTEGER", r"\d+"),
        ("ASSIGN", r"="),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("MUL", r"\*"),
        ("DIV", r"/"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SEMICOLON", r";"),
    ]

    TOKEN_TYPES: dict[str, TokenType] = {
        "IDENTIFIER": TokenType.IDENTIFIER,
        "INTEGER": TokenType.INTEGER,
        "ASSIGN": TokenType.ASSIGN,
        "PLUS": TokenType.PLUS,
        "MINUS": TokenType.MINUS,
        "MUL": TokenType.MUL,
        "DIV": TokenType.DIV,
        "LPAREN": TokenType.LPAREN,
        "RPAREN": TokenType.RPAREN,
        "SEMICOLON": TokenType.SEMICOLON,
    }

    MASTER_PATTERN = re.compile(
        "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_PATTERNS)
    )

    def __init__(self, source: str) -> None:
        self.source = source

    def tokenize(self) -> list[Token]:
        """Tokenize input text and return tokens ending with EOF."""
        tokens: list[Token] = []
        position = 0
        line = 1
        column = 1

        while position < len(self.source):
            match = self.MASTER_PATTERN.match(self.source, position)
            if match is None:
                invalid_char = self.source[position]
                raise LexerError(
                    f"Invalid character {invalid_char!r} at line {line}, column {column}."
                )

            lexeme = match.group(0)
            token_name = match.lastgroup
            start_line = line
            start_column = column

            line, column = self._advance_location(lexeme, line, column)
            position = match.end()

            if token_name == "WHITESPACE":
                continue

            if token_name is None or token_name not in self.TOKEN_TYPES:
                raise LexerError(
                    f"Internal lexer error: unrecognized token at line {start_line}, "
                    f"column {start_column}."
                )

            token_type = self.TOKEN_TYPES[token_name]
            literal = int(lexeme) if token_type == TokenType.INTEGER else None
            tokens.append(
                Token(
                    token_type=token_type,
                    lexeme=lexeme,
                    literal=literal,
                    line=start_line,
                    column=start_column,
                )
            )

        tokens.append(
            Token(
                token_type=TokenType.EOF,
                lexeme="",
                literal=None,
                line=line,
                column=column,
            )
        )
        return tokens

    @staticmethod
    def _advance_location(lexeme: str, line: int, column: int) -> tuple[int, int]:
        """
        Move line/column counters after consuming `lexeme`.

        Handles `\\n`, `\\r`, and `\\r\\n` newlines.
        """
        index = 0
        while index < len(lexeme):
            char = lexeme[index]

            if char == "\r":
                line += 1
                column = 1
                if index + 1 < len(lexeme) and lexeme[index + 1] == "\n":
                    index += 1
            elif char == "\n":
                line += 1
                column = 1
            else:
                column += 1

            index += 1

        return line, column
