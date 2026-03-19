"""Demo script: tokenize a mini-language program and print tokens."""

from __future__ import annotations

from lexer import Lexer


def main() -> None:
    """Run a sample lexing session and print all generated tokens."""
    sample_source = """
// Demo program for lexer
let x = 10
let y = 3.14
let name = "formal language"
if sin(x) >= y [ let flag = true ] else [ let flag = false ]
while x != 0 [ x = x - 1 ]
"""

    lexer = Lexer(sample_source)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"TokenType.{token.type.name:<10} | {token.value!s:<16} | {token.line}:{token.column}")


if __name__ == "__main__":
    main()
