"""Simple entry point: read source, tokenize it, parse it, and print the AST."""

from __future__ import annotations

import argparse
from pathlib import Path

from lexer.lexer import Lexer, LexerError
from parser.ast_nodes import pretty_print_ast
from parser.parser import Parser, ParserError


SAMPLE_PROGRAM = """\
x = 5 + 2 * (3 - 1);
y = x / 2;
z = y + 7;
"""


def load_source(file_path: str | None) -> str:
    """
    Load program text from a file path.

    If `file_path` is None, return the built-in sample program.
    """
    if file_path is None:
        return SAMPLE_PROGRAM

    path = Path(file_path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    """CLI entry point."""
    arg_parser = argparse.ArgumentParser(
        description="Run lexer and parser for the tiny assignment language."
    )
    arg_parser.add_argument(
        "file",
        nargs="?",
        help="Optional source file path. If omitted, a built-in sample is used.",
    )
    args = arg_parser.parse_args()

    try:
        source = load_source(args.file)
    except OSError as exc:
        print(f"File error: {exc}")
        return 1

    print("Input program:")
    print(source.rstrip())

    try:
        tokens = Lexer(source).tokenize()
    except LexerError as exc:
        print(f"Lexer error: {exc}")
        return 1

    print("\nTokens:")
    for token in tokens:
        print(f"  {token}")

    try:
        ast = Parser(tokens).parse()
    except ParserError as exc:
        print(f"Parser error: {exc}")
        return 1

    print("\nAST:")
    print(pretty_print_ast(ast))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
