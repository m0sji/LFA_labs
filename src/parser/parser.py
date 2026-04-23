"""Handwritten recursive descent parser for the tiny language."""

from __future__ import annotations

from lexer.token import Token
from lexer.token_type import TokenType
from parser.ast_nodes import (
    Assignment,
    BinaryOperation,
    Expression,
    ExpressionStatement,
    Identifier,
    Number,
    Program,
    Statement,
)


class ParserError(ValueError):
    """Raised when the token stream does not match the grammar."""


class Parser:
    """
    Recursive descent parser.

    Grammar:
        program         -> statement_list EOF
        statement_list  -> statement (';' statement)* ';'?
        statement       -> assignment | expression
        assignment      -> IDENTIFIER '=' expression
        expression      -> term (('+' | '-') term)*
        term            -> factor (('*' | '/') factor)*
        factor          -> INTEGER | IDENTIFIER | '(' expression ')'
    """

    def __init__(self, tokens: list[Token]) -> None:
        """Initialize parser with a token list produced by the lexer."""
        if not tokens:
            raise ParserError("Parser received an empty token stream.")
        self.tokens = tokens
        self.position = 0

    def parse(self) -> Program:
        """Parse the full token stream and return a `Program` AST node."""
        statements = self.parse_statement_list()

        if self.current_token.token_type != TokenType.EOF:
            token = self.current_token
            raise ParserError(
                "Expected ';' between statements, "
                f"got {token.token_type.name} at line {token.line}, column {token.column}."
            )

        self.eat(TokenType.EOF)
        return Program(statements=statements)

    def parse_statement_list(self) -> list[Statement]:
        """Parse one or more statements separated by semicolons."""
        statements: list[Statement] = []

        if self.current_token.token_type == TokenType.EOF:
            return statements

        statements.append(self.parse_statement())

        while self.current_token.token_type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            # Allow a trailing semicolon before EOF.
            if self.current_token.token_type == TokenType.EOF:
                break
            statements.append(self.parse_statement())

        return statements

    def parse_statement(self) -> Statement:
        """Parse a single statement: assignment or expression statement."""
        if self._is_assignment_start():
            return self.parse_assignment()

        return ExpressionStatement(expression=self.parse_expression())

    def parse_assignment(self) -> Assignment:
        """Parse `IDENTIFIER '=' expression`."""
        name_token = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        value = self.parse_expression()
        return Assignment(name=name_token.lexeme, value=value)

    def parse_expression(self) -> Expression:
        """Parse addition and subtraction (lower precedence)."""
        node = self.parse_term()

        while self.current_token.token_type in (TokenType.PLUS, TokenType.MINUS):
            operator_token = self.current_token
            self.eat(operator_token.token_type)
            right = self.parse_term()
            node = BinaryOperation(
                left=node,
                operator=operator_token.lexeme,
                right=right,
            )

        return node

    def parse_term(self) -> Expression:
        """Parse multiplication and division (higher precedence)."""
        node = self.parse_factor()

        while self.current_token.token_type in (TokenType.MUL, TokenType.DIV):
            operator_token = self.current_token
            self.eat(operator_token.token_type)
            right = self.parse_factor()
            node = BinaryOperation(
                left=node,
                operator=operator_token.lexeme,
                right=right,
            )

        return node

    def parse_factor(self) -> Expression:
        """Parse a number, identifier, or parenthesized expression."""
        token = self.current_token

        if token.token_type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            if token.literal is None:
                raise ParserError(
                    f"Invalid INTEGER literal at line {token.line}, column {token.column}."
                )
            return Number(value=token.literal)

        if token.token_type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Identifier(name=token.lexeme)

        if token.token_type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return node

        raise ParserError(
            "Expected INTEGER, IDENTIFIER, or '(' "
            f"at line {token.line}, column {token.column}, "
            f"got {token.token_type.name}."
        )

    def eat(self, expected_type: TokenType) -> Token:
        """Consume one token if it matches `expected_type`; otherwise raise error."""
        token = self.current_token
        if token.token_type != expected_type:
            raise ParserError(
                f"Expected {expected_type.name}, got {token.token_type.name} "
                f"at line {token.line}, column {token.column}."
            )

        self.position += 1
        return token

    @property
    def current_token(self) -> Token:
        """Return the current token or the last token when beyond input."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]

    def _next_token_type(self) -> TokenType | None:
        """Peek next token type without consuming the current token."""
        next_index = self.position + 1
        if next_index >= len(self.tokens):
            return None
        return self.tokens[next_index].token_type

    def _is_assignment_start(self) -> bool:
        """Return True when current position begins an assignment statement."""
        return (
            self.current_token.token_type == TokenType.IDENTIFIER
            and self._next_token_type() == TokenType.ASSIGN
        )
