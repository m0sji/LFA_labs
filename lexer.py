"""Lexer implementation for a small formal-languages lab language."""

from __future__ import annotations

from typing import Any

from tokens import Token, TokenType


class LexerError(Exception):
    """Raised when invalid or incomplete lexemes are encountered."""

    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column


class Lexer:
    """Converts source code text into a list of tokens."""

    KEYWORDS: dict[str, TokenType] = {
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "let": TokenType.LET,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "sin": TokenType.SIN,
        "cos": TokenType.COS,
        "tan": TokenType.TAN,
    }

    def __init__(self, source: str) -> None:
        """Initialize lexer state for one source string."""
        self.source = source
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """Tokenize the full source and return all tokens."""
        while not self._is_at_end():
            self._skip_whitespace_and_comments()
            if self._is_at_end():
                break

            ch = self._current_char()

            if ch.isdigit():
                self._scan_number()
                continue

            if ch == '"':
                self._scan_string()
                continue

            if ch.isalpha() or ch == "_":
                self._scan_identifier_or_keyword()
                continue

            start_line, start_column = self.line, self.column

            match ch:
                case "+":
                    self._advance()
                    self._add_token(TokenType.PLUS, "+", start_line, start_column)
                case "-":
                    self._advance()
                    self._add_token(TokenType.MINUS, "-", start_line, start_column)
                case "*":
                    self._advance()
                    self._add_token(TokenType.STAR, "*", start_line, start_column)
                case "/":
                    self._advance()
                    self._add_token(TokenType.SLASH, "/", start_line, start_column)
                case "^":
                    self._advance()
                    self._add_token(TokenType.CARET, "^", start_line, start_column)
                case "(":
                    self._advance()
                    self._add_token(TokenType.LPAREN, "(", start_line, start_column)
                case ")":
                    self._advance()
                    self._add_token(TokenType.RPAREN, ")", start_line, start_column)
                case "[":
                    self._advance()
                    self._add_token(TokenType.LBRACKET, "[", start_line, start_column)
                case "]":
                    self._advance()
                    self._add_token(TokenType.RBRACKET, "]", start_line, start_column)
                case "=":
                    self._scan_equals_related()
                case "!":
                    self._scan_bang_related()
                case "<":
                    self._scan_less_related()
                case ">":
                    self._scan_greater_related()
                case _:
                    raise LexerError(
                        f"Unrecognized character {ch!r}", start_line, start_column
                    )

        self._add_token(TokenType.EOF, None, self.line, self.column)
        return self.tokens

    def _scan_number(self) -> None:
        """Scan integer and float literals."""
        start_line, start_column = self.line, self.column
        start_index = self.index

        while self._current_char().isdigit():
            self._advance()
            if self._is_at_end():
                break

        is_float = False
        if not self._is_at_end() and self._current_char() == "." and self._peek().isdigit():
            is_float = True
            self._advance()  # Consume dot.
            while not self._is_at_end() and self._current_char().isdigit():
                self._advance()

        lexeme = self.source[start_index : self.index]
        if is_float:
            self._add_token(TokenType.FLOAT, float(lexeme), start_line, start_column)
        else:
            self._add_token(TokenType.INTEGER, int(lexeme), start_line, start_column)

    def _scan_string(self) -> None:
        """Scan a double-quoted string literal with simple escapes."""
        start_line, start_column = self.line, self.column
        self._advance()  # Consume opening quote.

        chars: list[str] = []
        while not self._is_at_end():
            ch = self._current_char()
            if ch == '"':
                self._advance()  # Consume closing quote.
                self._add_token(TokenType.STRING, "".join(chars), start_line, start_column)
                return

            if ch == "\\":
                self._advance()  # Consume backslash.
                if self._is_at_end():
                    raise LexerError("Unterminated string literal", start_line, start_column)
                escaped = self._current_char()
                chars.append(self._decode_escape(escaped, start_line, start_column))
                self._advance()
                continue

            if ch == "\n":
                raise LexerError("Unterminated string literal", start_line, start_column)

            chars.append(ch)
            self._advance()

        raise LexerError("Unterminated string literal", start_line, start_column)

    def _scan_identifier_or_keyword(self) -> None:
        """Scan identifiers and reserved words (keywords/functions/booleans)."""
        start_line, start_column = self.line, self.column
        start_index = self.index

        while not self._is_at_end() and (
            self._current_char().isalnum() or self._current_char() == "_"
        ):
            self._advance()

        lexeme = self.source[start_index : self.index]
        token_type = self.KEYWORDS.get(lexeme, TokenType.IDENTIFIER)

        if token_type is TokenType.TRUE:
            self._add_token(token_type, True, start_line, start_column)
        elif token_type is TokenType.FALSE:
            self._add_token(token_type, False, start_line, start_column)
        else:
            self._add_token(token_type, lexeme, start_line, start_column)

    def _scan_equals_related(self) -> None:
        """Scan '=' and '==' operators."""
        start_line, start_column = self.line, self.column
        self._advance()  # Consume '='.
        if not self._is_at_end() and self._current_char() == "=":
            self._advance()
            self._add_token(TokenType.EQ_EQ, "==", start_line, start_column)
        else:
            self._add_token(TokenType.ASSIGN, "=", start_line, start_column)

    def _scan_bang_related(self) -> None:
        """Scan '!=' operator and reject standalone '!'."""
        start_line, start_column = self.line, self.column
        self._advance()  # Consume '!'.
        if not self._is_at_end() and self._current_char() == "=":
            self._advance()
            self._add_token(TokenType.BANG_EQ, "!=", start_line, start_column)
            return
        raise LexerError("Unexpected '!': expected '!='", start_line, start_column)

    def _scan_less_related(self) -> None:
        """Scan '<' and '<=' operators."""
        start_line, start_column = self.line, self.column
        self._advance()
        if not self._is_at_end() and self._current_char() == "=":
            self._advance()
            self._add_token(TokenType.LT_EQ, "<=", start_line, start_column)
        else:
            self._add_token(TokenType.LT, "<", start_line, start_column)

    def _scan_greater_related(self) -> None:
        """Scan '>' and '>=' operators."""
        start_line, start_column = self.line, self.column
        self._advance()
        if not self._is_at_end() and self._current_char() == "=":
            self._advance()
            self._add_token(TokenType.GT_EQ, ">=", start_line, start_column)
        else:
            self._add_token(TokenType.GT, ">", start_line, start_column)

    def _skip_whitespace_and_comments(self) -> None:
        """Skip whitespace/newlines and single-line comments."""
        while not self._is_at_end():
            ch = self._current_char()

            # Consume all standard spacing characters.
            if ch in {" ", "\t", "\r", "\n"}:
                self._advance()
                continue

            # Skip // comment text until the end of the line.
            if ch == "/" and self._peek() == "/":
                self._advance()
                self._advance()
                while not self._is_at_end() and self._current_char() != "\n":
                    self._advance()
                continue

            break

    def _decode_escape(self, escaped: str, line: int, column: int) -> str:
        """Map supported escape sequences to their characters."""
        escapes: dict[str, str] = {
            '"': '"',
            "\\": "\\",
            "n": "\n",
            "t": "\t",
            "r": "\r",
        }
        if escaped not in escapes:
            raise LexerError(f"Unsupported escape sequence '\\{escaped}'", line, column)
        return escapes[escaped]

    def _add_token(self, token_type: TokenType, value: Any, line: int, column: int) -> None:
        """Append one token to the output list."""
        self.tokens.append(Token(token_type, value, line, column))

    def _current_char(self) -> str:
        """Return the character at the current index."""
        return self.source[self.index]

    def _peek(self) -> str:
        """Return the next character without consuming it."""
        next_index = self.index + 1
        if next_index >= self.length:
            return "\0"
        return self.source[next_index]

    def _advance(self) -> str:
        """Consume one character and update line/column counters."""
        ch = self.source[self.index]
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _is_at_end(self) -> bool:
        """Check if the cursor reached source end."""
        return self.index >= self.length
