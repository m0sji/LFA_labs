"""Simple unit tests for lexer tokenization."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from lexer.lexer import Lexer, LexerError
from lexer.token_type import TokenType


class TestLexer(unittest.TestCase):
    """Checks basic token recognition and lexer errors."""

    def test_identifiers_are_recognized(self) -> None:
        tokens = Lexer("alpha _beta gamma1").tokenize()
        self.assertEqual(
            [token.token_type for token in tokens],
            [
                TokenType.IDENTIFIER,
                TokenType.IDENTIFIER,
                TokenType.IDENTIFIER,
                TokenType.EOF,
            ],
        )
        self.assertEqual([tokens[0].lexeme, tokens[1].lexeme, tokens[2].lexeme], ["alpha", "_beta", "gamma1"])

    def test_integers_are_recognized(self) -> None:
        tokens = Lexer("1 23 456").tokenize()
        self.assertEqual(
            [token.token_type for token in tokens],
            [TokenType.INTEGER, TokenType.INTEGER, TokenType.INTEGER, TokenType.EOF],
        )
        self.assertEqual([tokens[0].literal, tokens[1].literal, tokens[2].literal], [1, 23, 456])

    def test_operators_and_punctuation_are_recognized(self) -> None:
        tokens = Lexer("= + - * / ( ) ;").tokenize()
        self.assertEqual(
            [token.token_type for token in tokens],
            [
                TokenType.ASSIGN,
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.MUL,
                TokenType.DIV,
                TokenType.LPAREN,
                TokenType.RPAREN,
                TokenType.SEMICOLON,
                TokenType.EOF,
            ],
        )

    def test_invalid_character_raises_error(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("x = 1 @ 2;").tokenize()


if __name__ == "__main__":
    unittest.main()
