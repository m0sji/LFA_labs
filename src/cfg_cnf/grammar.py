"""Generic grammar data model and utility methods."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple, Union

Symbol = str
ProductionRHS = Tuple[Symbol, ...]
ProductionInput = Union[str, Sequence[Symbol]]


@dataclass
class Grammar:
    """
    Store a context-free grammar in a generic, reusable form.

    Attributes:
        nonterminals: Set of nonterminal symbols (V_N).
        terminals: Set of terminal symbols (V_T).
        productions: Mapping from LHS nonterminal to a list of RHS alternatives.
                     Each RHS alternative is stored as a tuple of symbols.
        start_symbol: Start symbol of the grammar.
    """

    nonterminals: set[Symbol] = field(default_factory=set)
    terminals: set[Symbol] = field(default_factory=set)
    productions: Dict[Symbol, List[ProductionRHS]] = field(default_factory=dict)
    start_symbol: Symbol = ""

    EPSILON: str = "\u03b5"

    def __post_init__(self) -> None:
        """Normalize internal containers after initialization."""
        self.nonterminals = set(self.nonterminals)
        self.terminals = set(self.terminals)
        self.productions = {
            lhs: [tuple(rhs) for rhs in rhs_list]
            for lhs, rhs_list in self.productions.items()
        }
        if self.start_symbol and self.start_symbol not in self.nonterminals:
            self.nonterminals.add(self.start_symbol)

    @classmethod
    def from_dict(
        cls,
        *,
        nonterminals: Iterable[Symbol],
        terminals: Iterable[Symbol],
        productions: Mapping[Symbol, Union[str, Iterable[ProductionInput]]],
        start_symbol: Symbol,
    ) -> "Grammar":
        """
        Build a Grammar object from a Python dictionary.

        Args:
            nonterminals: Iterable of nonterminal symbols.
            terminals: Iterable of terminal symbols.
            productions: Mapping from LHS to RHS alternatives. RHS can be:
                - A single string with optional `|` separators, e.g. "aB | bA | B"
                - An iterable of alternatives, where each alternative is:
                    - a compact string, e.g. "aB"
                    - a spaced string, e.g. "a B"
                    - a sequence of symbol tokens, e.g. ("a", "B")
            start_symbol: The start symbol of the grammar.
        """
        grammar = cls(
            nonterminals=set(nonterminals),
            terminals=set(terminals),
            start_symbol=start_symbol,
        )

        for lhs, rhs_values in productions.items():
            alternatives: List[ProductionInput]
            if isinstance(rhs_values, str):
                alternatives = [part.strip() for part in rhs_values.split("|")]
            else:
                alternatives = list(rhs_values)

            for rhs in alternatives:
                grammar.add_production(lhs, rhs)

        return grammar

    def add_production(self, lhs: Symbol, rhs: ProductionInput) -> None:
        """
        Add a production rule of the form `lhs -> rhs`.

        Args:
            lhs: Left-hand side nonterminal.
            rhs: Right-hand side alternative, as string or sequence of symbols.
        """
        if lhs not in self.nonterminals:
            raise ValueError(f"LHS symbol '{lhs}' is not listed in nonterminals.")

        normalized_rhs = self._normalize_rhs(rhs)
        self.productions.setdefault(lhs, [])
        if normalized_rhs not in self.productions[lhs]:
            self.productions[lhs].append(normalized_rhs)

    def pretty(self) -> str:
        """
        Return a human-readable representation of the grammar.

        Returns:
            Multi-line string with VN/VT sets, start symbol, and productions.
        """
        lines = [
            f"V_N = {{{', '.join(sorted(self.nonterminals))}}}",
            f"V_T = {{{', '.join(sorted(self.terminals))}}}",
            f"Start = {self.start_symbol}",
            "Productions:",
        ]

        for lhs in self._ordered_nonterminals():
            rhs_options = self.productions.get(lhs, [])
            if not rhs_options:
                continue
            rendered_rhs = " | ".join(self._format_rhs(rhs) for rhs in rhs_options)
            lines.append(f"{lhs} -> {rendered_rhs}")

        return "\n".join(lines)

    def _ordered_nonterminals(self) -> List[Symbol]:
        """Return nonterminals with start symbol first for stable pretty printing."""
        items = sorted(self.nonterminals)
        if self.start_symbol in items:
            items.remove(self.start_symbol)
            items.insert(0, self.start_symbol)
        return items

    def _normalize_rhs(self, rhs: ProductionInput) -> ProductionRHS:
        """
        Normalize one RHS alternative into a tuple of symbols.

        The epsilon production is represented internally as an empty tuple.
        """
        if isinstance(rhs, str):
            token = rhs.strip()
            if token in {"", self.EPSILON}:
                return tuple()
            if "|" in token:
                raise ValueError("add_production expects a single RHS alternative.")
            if " " in token:
                symbols = tuple(part for part in token.split() if part)
                return tuple() if symbols == (self.EPSILON,) else symbols
            return self._tokenize_compact_rhs(token)

        symbols = tuple(str(part).strip() for part in rhs if str(part).strip())
        return tuple() if symbols == (self.EPSILON,) else symbols

    def _tokenize_compact_rhs(self, text: str) -> ProductionRHS:
        """
        Tokenize compact RHS strings like `aB` using known grammar symbols.

        Notes:
            - Uses longest-match scanning over VN U VT.
            - Falls back to single-character tokens for unknown segments.
        """
        symbol_pool = sorted(self.nonterminals | self.terminals, key=len, reverse=True)
        if not symbol_pool:
            return tuple(text)

        result: List[Symbol] = []
        index = 0
        while index < len(text):
            matched: Symbol | None = None
            for symbol in symbol_pool:
                if text.startswith(symbol, index):
                    matched = symbol
                    break

            if matched is None:
                matched = text[index]

            result.append(matched)
            index += len(matched)

        return tuple(result)

    def _format_rhs(self, rhs: ProductionRHS) -> str:
        """Format one RHS alternative for display."""
        if not rhs:
            return self.EPSILON
        if all(len(symbol) == 1 for symbol in rhs):
            return "".join(rhs)
        return " ".join(rhs)

    def __str__(self) -> str:
        """Return pretty representation when printing the object."""
        return self.pretty()
