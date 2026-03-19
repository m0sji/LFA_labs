"""Unit tests for lexer.py."""

from __future__ import annotations

import pytest

from lexer import Lexer, LexerError
from tokens import TokenType


def test_tokenize_valid_program() -> None:
    source = 'let a = 12 + 3.5 * sin(x) != 0 [ let ok = true ] else [ let ok = false ]'
    tokens = Lexer(source).tokenize()

    token_types = [token.type for token in tokens]
    expected = [
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.INTEGER,
        TokenType.PLUS,
        TokenType.FLOAT,
        TokenType.STAR,
        TokenType.SIN,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.BANG_EQ,
        TokenType.INTEGER,
        TokenType.LBRACKET,
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.TRUE,
        TokenType.RBRACKET,
        TokenType.ELSE,
        TokenType.LBRACKET,
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.FALSE,
        TokenType.RBRACKET,
        TokenType.EOF,
    ]

    assert token_types == expected
    assert tokens[3].value == 12
    assert tokens[5].value == 3.5
    assert tokens[17].value is True
    assert tokens[24].value is False


def test_comments_strings_and_positions() -> None:
    source = '// first line comment\nlet msg = "hi\\nthere" // inline comment\nmsg = "ok"'
    tokens = Lexer(source).tokenize()

    assert [t.type for t in tokens] == [
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.STRING,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.STRING,
        TokenType.EOF,
    ]

    # "let" starts on line 2, column 1 after the first comment line.
    assert tokens[0].line == 2
    assert tokens[0].column == 1
    assert tokens[3].value == "hi\nthere"
    assert tokens[4].line == 3
    assert tokens[4].column == 1


def test_raises_on_unrecognized_character() -> None:
    with pytest.raises(LexerError) as exc:
        Lexer("let x = @").tokenize()

    assert "Unrecognized character '@'" in str(exc.value)
    assert "line 1, column 9" in str(exc.value)


def test_raises_on_unterminated_string() -> None:
    with pytest.raises(LexerError) as exc:
        Lexer('let s = "unterminated').tokenize()

    assert "Unterminated string literal" in str(exc.value)
