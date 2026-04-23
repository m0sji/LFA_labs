"""AST node definitions for the tiny assignment/expression language."""

from __future__ import annotations

from dataclasses import dataclass


class ASTNode:
    """
    Base class for all AST nodes.

    Dataclasses provide readable ``__repr__`` output for debugging.
    """


class Statement(ASTNode):
    """Base class for statement nodes."""


class Expression(ASTNode):
    """Base class for expression nodes."""


@dataclass(slots=True)
class Program(ASTNode):
    """Root node that stores all statements in source order."""

    statements: list[Statement]


@dataclass(slots=True)
class Assignment(Statement):
    """Assignment statement: variable name on the left, expression on the right."""

    name: str
    value: Expression


@dataclass(slots=True)
class BinaryOperation(Expression):
    """Binary arithmetic operation (e.g., ``a + b`` or ``x * y``)."""

    left: Expression
    operator: str
    right: Expression


@dataclass(slots=True)
class Number(Expression):
    """Integer number literal."""

    value: int


@dataclass(slots=True)
class Identifier(Expression):
    """Variable reference used in expressions."""

    name: str


# Optional node to keep statement grammar flexible (`statement -> expression`).
@dataclass(slots=True)
class ExpressionStatement(Statement):
    """Statement consisting of a single expression."""

    expression: Expression


def pretty_print_ast(node: ASTNode) -> str:
    """
    Return a readable hierarchical tree for AST nodes.

    Core node output format:
    - Program
    - Assignment
      - Identifier(name)
      - expression subtree
    - BinaryOperation(op)
    - Number(value)
    - Identifier(name)
    """

    lines: list[str] = []

    def visit(current: ASTNode, indent: int) -> None:
        prefix = "  " * indent

        if isinstance(current, Program):
            lines.append(f"{prefix}Program")
            for statement in current.statements:
                visit(statement, indent + 1)
            return

        if isinstance(current, Assignment):
            lines.append(f"{prefix}Assignment")
            lines.append(f"{'  ' * (indent + 1)}Identifier({current.name})")
            visit(current.value, indent + 1)
            return

        if isinstance(current, BinaryOperation):
            lines.append(f"{prefix}BinaryOperation({current.operator})")
            visit(current.left, indent + 1)
            visit(current.right, indent + 1)
            return

        if isinstance(current, Number):
            lines.append(f"{prefix}Number({current.value})")
            return

        if isinstance(current, Identifier):
            lines.append(f"{prefix}Identifier({current.name})")
            return

        if isinstance(current, ExpressionStatement):
            lines.append(f"{prefix}ExpressionStatement")
            visit(current.expression, indent + 1)
            return

        lines.append(f"{prefix}{type(current).__name__}")

    visit(node, 0)
    return "\n".join(lines)


__all__ = [
    "ASTNode",
    "Statement",
    "Expression",
    "Program",
    "Assignment",
    "BinaryOperation",
    "Number",
    "Identifier",
    "ExpressionStatement",
    "pretty_print_ast",
]
