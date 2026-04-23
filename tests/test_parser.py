"""Simple unit tests for parser behavior."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from lexer.lexer import Lexer
from parser.ast_nodes import (
    Assignment,
    BinaryOperation,
    ExpressionStatement,
    Number,
    Program,
)
from parser.parser import Parser


def parse_program(source: str) -> Program:
    """Lex and parse source into a Program AST."""
    return Parser(Lexer(source).tokenize()).parse()


class TestParser(unittest.TestCase):
    """Checks assignment parsing and expression structure."""

    def test_assignment_statement_parses_correctly(self) -> None:
        program = parse_program("x = 5;")
        self.assertEqual(len(program.statements), 1)

        assignment = program.statements[0]
        self.assertIsInstance(assignment, Assignment)
        self.assertEqual(assignment.name, "x")
        self.assertIsInstance(assignment.value, Number)
        self.assertEqual(assignment.value.value, 5)

    def test_operator_precedence_mul_before_add(self) -> None:
        program = parse_program("x = 2 + 3 * 4;")
        assignment = program.statements[0]
        self.assertIsInstance(assignment, Assignment)

        root = assignment.value
        self.assertIsInstance(root, BinaryOperation)
        self.assertEqual(root.operator, "+")
        self.assertIsInstance(root.left, Number)
        self.assertEqual(root.left.value, 2)

        self.assertIsInstance(root.right, BinaryOperation)
        self.assertEqual(root.right.operator, "*")
        self.assertEqual(root.right.left.value, 3)
        self.assertEqual(root.right.right.value, 4)

    def test_parentheses_affect_precedence(self) -> None:
        program = parse_program("x = (2 + 3) * 4;")
        assignment = program.statements[0]
        self.assertIsInstance(assignment, Assignment)

        root = assignment.value
        self.assertIsInstance(root, BinaryOperation)
        self.assertEqual(root.operator, "*")
        self.assertIsInstance(root.right, Number)
        self.assertEqual(root.right.value, 4)

        self.assertIsInstance(root.left, BinaryOperation)
        self.assertEqual(root.left.operator, "+")
        self.assertEqual(root.left.left.value, 2)
        self.assertEqual(root.left.right.value, 3)

    def test_multiple_statements_are_parsed(self) -> None:
        program = parse_program("a = 1; b = a + 2; c = b * 3;")
        self.assertEqual(len(program.statements), 3)
        self.assertEqual(program.statements[0].name, "a")
        self.assertEqual(program.statements[1].name, "b")
        self.assertEqual(program.statements[2].name, "c")

    def test_expression_statement_is_supported(self) -> None:
        program = parse_program("2 + 3 * 4;")
        self.assertEqual(len(program.statements), 1)
        self.assertIsInstance(program.statements[0], ExpressionStatement)


if __name__ == "__main__":
    unittest.main()
