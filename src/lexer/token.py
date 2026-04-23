"""Token model shared between lexer and parser."""

from dataclasses import dataclass

from lexer.token_type import TokenType


@dataclass(frozen=True, slots=True)
class Token:
    """Represents one lexical token with source location."""

    token_type: TokenType
    lexeme: str
    literal: int | None
    line: int
    column: int

    def __str__(self) -> str:
        """Return a compact human-readable form, useful in debugging output."""
        return (
            f"{self.token_type.name}(lexeme={self.lexeme!r}, literal={self.literal!r}, "
            f"line={self.line}, column={self.column})"
        )
