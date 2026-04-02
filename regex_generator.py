import random
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


STAR_MIN, STAR_MAX = 0, 5
PLUS_MIN, PLUS_MAX = 1, 5


@dataclass(frozen=True)
class Token:
    kind: str
    value: Optional[int | str] = None
    position: int = -1


class RegexTokenizer:
    """
    Tokenizer for the supported regex subset.
    Whitespace is ignored.
    """

    def __init__(self, pattern: str):
        self.pattern = pattern

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        i = 0
        n = len(self.pattern)

        while i < n:
            ch = self.pattern[i]

            if ch.isspace():
                i += 1
                continue

            if ch == "(":
                tokens.append(Token("LPAREN", position=i))
                i += 1
                continue
            if ch == ")":
                tokens.append(Token("RPAREN", position=i))
                i += 1
                continue
            if ch == "|":
                tokens.append(Token("ALT", position=i))
                i += 1
                continue
            if ch == "*":
                tokens.append(Token("STAR", position=i))
                i += 1
                continue
            if ch == "+":
                tokens.append(Token("PLUS", position=i))
                i += 1
                continue
            if ch == "?":
                tokens.append(Token("QMARK", position=i))
                i += 1
                continue
            if ch == "^":
                exact, next_index = self._read_exact_count(i)
                tokens.append(Token("EXACT", value=exact, position=i))
                i = next_index
                continue

            tokens.append(Token("LITERAL", value=ch, position=i))
            i += 1

        tokens.append(Token("EOF", position=n))
        return tokens

    def _read_exact_count(self, caret_index: int) -> Tuple[int, int]:
        """
        Reads ^n (single digit) or ^{n} (multi-digit extension).
        Returns: (count, next_index_after_quantifier)
        """
        n = len(self.pattern)
        i = caret_index + 1

        if i >= n:
            raise ValueError(f"Expected repetition count after '^' at position {caret_index}")

        # Extension: ^{12}
        if self.pattern[i] == "{":
            j = i + 1
            while j < n and self.pattern[j].isdigit():
                j += 1
            if j == i + 1 or j >= n or self.pattern[j] != "}":
                raise ValueError(f"Invalid ^{{n}} quantifier at position {caret_index}")
            return int(self.pattern[i + 1 : j]), j + 1

        # Required behavior: single-digit ^n.
        if self.pattern[i].isdigit():
            return int(self.pattern[i]), i + 1

        raise ValueError(f"Expected digit after '^' at position {caret_index}")


class ASTNode:
    def generate(
        self,
        rng: random.Random,
        trace: Optional[List[str]] = None,
        level: int = 0,
    ) -> str:
        raise NotImplementedError

    def to_python_regex(self) -> str:
        raise NotImplementedError


@dataclass
class Literal(ASTNode):
    char: str

    def generate(
        self,
        rng: random.Random,
        trace: Optional[List[str]] = None,
        level: int = 0,
    ) -> str:
        if trace is not None:
            trace.append(f"{'  ' * level}Literal('{self.char}') -> '{self.char}'")
        return self.char

    def to_python_regex(self) -> str:
        return re.escape(self.char)


@dataclass
class Concat(ASTNode):
    parts: List[ASTNode]

    def generate(
        self,
        rng: random.Random,
        trace: Optional[List[str]] = None,
        level: int = 0,
    ) -> str:
        if trace is not None:
            trace.append(f"{'  ' * level}Concat start ({len(self.parts)} parts)")

        out = "".join(part.generate(rng, trace, level + 1) for part in self.parts)

        if trace is not None:
            trace.append(f"{'  ' * level}Concat result -> '{out}'")
        return out

    def to_python_regex(self) -> str:
        return "".join(part.to_python_regex() for part in self.parts)


@dataclass
class Alternate(ASTNode):
    options: List[ASTNode]

    def generate(
        self,
        rng: random.Random,
        trace: Optional[List[str]] = None,
        level: int = 0,
    ) -> str:
        idx = rng.randrange(len(self.options))
        if trace is not None:
            trace.append(f"{'  ' * level}Alternate choose option {idx + 1}/{len(self.options)}")

        out = self.options[idx].generate(rng, trace, level + 1)

        if trace is not None:
            trace.append(f"{'  ' * level}Alternate result -> '{out}'")
        return out

    def to_python_regex(self) -> str:
        return "(?:" + "|".join(option.to_python_regex() for option in self.options) + ")"


@dataclass
class Repeat(ASTNode):
    node: ASTNode
    minimum: int
    maximum: int

    def generate(
        self,
        rng: random.Random,
        trace: Optional[List[str]] = None,
        level: int = 0,
    ) -> str:
        count = rng.randint(self.minimum, self.maximum)

        if trace is not None:
            if self.minimum == self.maximum:
                trace.append(f"{'  ' * level}Repeat exact {count} times")
            else:
                trace.append(
                    f"{'  ' * level}Repeat range [{self.minimum}, {self.maximum}] chose {count}"
                )

        out = "".join(self.node.generate(rng, trace, level + 1) for _ in range(count))

        if trace is not None:
            trace.append(f"{'  ' * level}Repeat result -> '{out}'")
        return out

    def to_python_regex(self) -> str:
        inner = "(?:" + self.node.to_python_regex() + ")"
        if self.minimum == self.maximum:
            return f"{inner}{{{self.minimum}}}"
        return f"{inner}{{{self.minimum},{self.maximum}}}"


class RegexParser:
    """
    Recursive-descent parser with precedence:
    1) Quantifiers (* + ? ^n)
    2) Concatenation
    3) Alternation (|)
    """

    QUANTIFIER_KINDS = {"STAR", "PLUS", "QMARK", "EXACT"}

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ASTNode:
        node = self._parse_expression()
        self._expect("EOF")
        return node

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        token = self._current()
        self.pos += 1
        return token

    def _match(self, kind: str) -> Optional[Token]:
        if self._current().kind == kind:
            return self._advance()
        return None

    def _expect(self, kind: str) -> Token:
        token = self._match(kind)
        if token is None:
            current = self._current()
            raise ValueError(f"Expected {kind} at position {current.position}, got {current.kind}")
        return token

    def _parse_expression(self) -> ASTNode:
        return self._parse_alternation()

    def _parse_alternation(self) -> ASTNode:
        options = [self._parse_concatenation()]
        while self._match("ALT") is not None:
            options.append(self._parse_concatenation())
        if len(options) == 1:
            return options[0]
        return Alternate(options)

    def _parse_concatenation(self) -> ASTNode:
        parts: List[ASTNode] = []

        while self._can_start_primary(self._current().kind):
            parts.append(self._parse_quantified())

        # Allows empty sides in alternation, e.g. (a|).
        if not parts:
            return Concat([])
        if len(parts) == 1:
            return parts[0]
        return Concat(parts)

    @staticmethod
    def _can_start_primary(kind: str) -> bool:
        return kind in {"LITERAL", "LPAREN"}

    def _parse_quantified(self) -> ASTNode:
        node = self._parse_primary()

        token = self._current()
        if token.kind == "STAR":
            self._advance()
            return Repeat(node=node, minimum=STAR_MIN, maximum=STAR_MAX)
        if token.kind == "PLUS":
            self._advance()
            return Repeat(node=node, minimum=PLUS_MIN, maximum=PLUS_MAX)
        if token.kind == "QMARK":
            self._advance()
            return Repeat(node=node, minimum=0, maximum=1)
        if token.kind == "EXACT":
            self._advance()
            exact = int(token.value)  # type: ignore[arg-type]
            return Repeat(node=node, minimum=exact, maximum=exact)
        return node

    def _parse_primary(self) -> ASTNode:
        token = self._current()

        if token.kind == "LITERAL":
            self._advance()
            return Literal(char=str(token.value))

        if token.kind == "LPAREN":
            self._advance()
            node = self._parse_expression()
            self._expect("RPAREN")
            return node

        if token.kind in self.QUANTIFIER_KINDS:
            raise ValueError(
                f"Quantifier {token.kind} has no target at position {token.position}"
            )

        raise ValueError(f"Unexpected token {token.kind} at position {token.position}")


def parse_regex(pattern: str) -> ASTNode:
    tokens = RegexTokenizer(pattern).tokenize()
    return RegexParser(tokens).parse()


def generate_random_string(ast: ASTNode, rng: Optional[random.Random] = None) -> str:
    rng = rng or random.Random()
    return ast.generate(rng)


def generate_with_steps(
    ast: ASTNode,
    rng: Optional[random.Random] = None,
) -> Tuple[str, List[str]]:
    rng = rng or random.Random()
    steps: List[str] = []
    generated = ast.generate(rng, trace=steps)
    return generated, steps


def generate_many(ast: ASTNode, count: int, rng: Optional[random.Random] = None) -> List[str]:
    rng = rng or random.Random()
    return [ast.generate(rng) for _ in range(count)]


def validate_samples(ast: ASTNode, samples: List[str]) -> bool:
    """
    Validates generated strings using a Python regex derived from the AST.
    """
    py_pattern = "^" + ast.to_python_regex() + "$"
    compiled = re.compile(py_pattern)
    return all(compiled.fullmatch(sample) is not None for sample in samples)


def print_outputs_for_regex(
    pattern: str,
    count: int = 10,
    seed: Optional[int] = None,
    show_steps: bool = True,
) -> None:
    count = max(10, count)
    ast = parse_regex(pattern)
    rng = random.Random(seed)
    samples = generate_many(ast, count, rng)

    print(f"Regex: {pattern}")
    print(f"Example outputs (count={count}, seed={seed}):")
    for i, sample in enumerate(samples, start=1):
        print(f"{i:2d}. {sample}")

    print(f"Validation: {'OK' if validate_samples(ast, samples) else 'FAILED'}")

    if show_steps:
        demo, steps = generate_with_steps(ast, rng)
        print("\nStep-by-step generation:")
        for step in steps:
            print(step)
        print(f"Final: {demo}")

    print("-" * 60)


def main() -> None:
    regex_patterns = [
        "(a|b)(c|d)E+G?",
        "P(Q|R|S)T(UV|W|X)*Z+",
        "1(0|1)*2(3|4)^536",  # Interpreted as: 1(0|1)*2(3|4)^5 36
    ]

    base_seed = 2026
    for i, pattern in enumerate(regex_patterns):
        print_outputs_for_regex(
            pattern=pattern,
            count=10,
            seed=base_seed + i,
            show_steps=True,
        )


if __name__ == "__main__":
    main()
