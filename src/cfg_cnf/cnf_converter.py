"""Skeleton CNF conversion workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from .grammar import Grammar, ProductionRHS, Symbol


@dataclass
class CNFConverter:
    """
    Transform a context-free grammar into Chomsky Normal Form (CNF).

    This class currently provides method skeletons only.
    """

    grammar: Grammar

    def to_cnf(self) -> Grammar:
        """
        Execute the full conversion pipeline and return a CNF grammar.

        Pipeline target (to be implemented):
            1. Remove epsilon productions
            2. Remove unit productions
            3. Remove useless symbols
            4. Replace terminals in long productions
            5. Binarize productions with length > 2
        """
        self.remove_epsilon_productions()
        self.remove_unit_productions()
        self.remove_useless_symbols()
        self.replace_terminals_in_long_rules()
        self.binarize_long_productions()
        return self.grammar

    def remove_epsilon_productions(self) -> "CNFConverter":
        """
        Eliminate epsilon productions while preserving language constraints.

        Returns:
            Self, so pipeline calls can be chained.
        """
        nullable = self.find_nullable_symbols()
        start_symbol = self.grammar.start_symbol
        start_is_nullable = start_symbol in nullable

        new_productions: Dict[Symbol, List[ProductionRHS]] = {
            lhs: [] for lhs in self.grammar.nonterminals
        }

        for lhs in sorted(self.grammar.nonterminals):
            for rhs in self.grammar.productions.get(lhs, []):
                if not rhs:
                    # Drop explicit epsilon productions; add back only for nullable start.
                    continue

                for candidate_rhs in self._generate_rhs_without_nullable(rhs, nullable):
                    if not candidate_rhs and lhs != start_symbol:
                        # Only start symbol is allowed to keep epsilon after elimination.
                        continue
                    self._add_unique_rhs(new_productions[lhs], candidate_rhs)

        if start_is_nullable:
            self._add_unique_rhs(new_productions[start_symbol], tuple())

        self.grammar.productions = {
            lhs: rhs_list for lhs, rhs_list in new_productions.items() if rhs_list
        }
        return self

    def find_nullable_symbols(self) -> Set[Symbol]:
        """
        Compute the nullable nonterminals using fixed-point iteration.

        A nonterminal is nullable if:
            - it has a direct epsilon production, or
            - it has a production where every symbol is nullable.
        """
        nullable: Set[Symbol] = set()
        changed = True

        while changed:
            changed = False
            for lhs, rhs_list in self.grammar.productions.items():
                if lhs in nullable:
                    continue

                for rhs in rhs_list:
                    if not rhs:
                        nullable.add(lhs)
                        changed = True
                        break

                    if all(symbol in nullable for symbol in rhs):
                        nullable.add(lhs)
                        changed = True
                        break

        return nullable

    def _generate_rhs_without_nullable(
        self, rhs: ProductionRHS, nullable: Set[Symbol]
    ) -> List[ProductionRHS]:
        """
        Generate all RHS variants by optionally removing nullable symbols.

        This preserves language behavior while eliminating epsilon productions.
        """
        nullable_positions = [idx for idx, symbol in enumerate(rhs) if symbol in nullable]
        total_masks = 1 << len(nullable_positions)
        variants: List[ProductionRHS] = []

        for mask in range(total_masks):
            removed = {
                nullable_positions[bit]
                for bit in range(len(nullable_positions))
                if mask & (1 << bit)
            }
            candidate = tuple(
                symbol for idx, symbol in enumerate(rhs) if idx not in removed
            )
            variants.append(candidate)

        return variants

    @staticmethod
    def _add_unique_rhs(bucket: List[ProductionRHS], rhs: ProductionRHS) -> None:
        """Append RHS only if it is not already present."""
        if rhs not in bucket:
            bucket.append(rhs)

    def remove_unit_productions(self) -> "CNFConverter":
        """
        Eliminate unit productions (A -> B).

        Returns:
            Self, so pipeline calls can be chained.
        """
        unit_pairs = self.compute_unit_pairs()

        reachable_by_lhs: Dict[Symbol, Set[Symbol]] = {
            lhs: set() for lhs in self.grammar.nonterminals
        }
        for src, dst in unit_pairs:
            reachable_by_lhs.setdefault(src, set()).add(dst)

        new_productions: Dict[Symbol, List[ProductionRHS]] = {}
        for lhs in sorted(self.grammar.nonterminals):
            collected: List[ProductionRHS] = []

            for target in sorted(reachable_by_lhs.get(lhs, {lhs})):
                for rhs in self.grammar.productions.get(target, []):
                    if self._is_unit_production(rhs):
                        continue
                    self._add_unique_rhs(collected, rhs)

            if collected:
                new_productions[lhs] = collected

        self.grammar.productions = new_productions
        return self

    def compute_unit_pairs(self) -> Set[Tuple[Symbol, Symbol]]:
        """
        Compute all unit pairs (A, B) such that A =>* B through unit productions.

        Includes reflexive pairs (A, A) for every nonterminal.
        """
        adjacency: Dict[Symbol, Set[Symbol]] = {
            nt: set() for nt in self.grammar.nonterminals
        }
        for lhs, rhs_list in self.grammar.productions.items():
            for rhs in rhs_list:
                if self._is_unit_production(rhs):
                    adjacency.setdefault(lhs, set()).add(rhs[0])

        unit_pairs: Set[Tuple[Symbol, Symbol]] = set()
        for src in self.grammar.nonterminals:
            visited: Set[Symbol] = {src}
            stack: List[Symbol] = [src]

            while stack:
                current = stack.pop()
                unit_pairs.add((src, current))
                for nxt in adjacency.get(current, set()):
                    if nxt not in visited:
                        visited.add(nxt)
                        stack.append(nxt)

        return unit_pairs

    def _is_unit_production(self, rhs: ProductionRHS) -> bool:
        """
        Check whether RHS is a unit production body (single nonterminal).
        """
        return len(rhs) == 1 and rhs[0] in self.grammar.nonterminals

    def remove_inaccessible_symbols(self) -> "CNFConverter":
        """
        Remove symbols not reachable from the start symbol.

        Returns:
            Self, so pipeline calls can be chained.
        """
        accessible_nonterminals = self.compute_accessible_nonterminals()

        new_productions: Dict[Symbol, List[ProductionRHS]] = {}
        for lhs in sorted(accessible_nonterminals):
            collected: List[ProductionRHS] = []
            for rhs in self.grammar.productions.get(lhs, []):
                if any(
                    symbol in self.grammar.nonterminals
                    and symbol not in accessible_nonterminals
                    for symbol in rhs
                ):
                    continue
                self._add_unique_rhs(collected, rhs)

            if collected:
                new_productions[lhs] = collected

        self.grammar.nonterminals = set(accessible_nonterminals)
        self.grammar.productions = new_productions
        self._refresh_terminals_from_productions()
        return self

    def compute_accessible_nonterminals(self) -> Set[Symbol]:
        """
        Compute nonterminals accessible from the start symbol.
        """
        if self.grammar.start_symbol not in self.grammar.nonterminals:
            return set()

        accessible: Set[Symbol] = {self.grammar.start_symbol}
        stack: List[Symbol] = [self.grammar.start_symbol]

        while stack:
            current = stack.pop()
            for rhs in self.grammar.productions.get(current, []):
                for symbol in rhs:
                    if (
                        symbol in self.grammar.nonterminals
                        and symbol not in accessible
                    ):
                        accessible.add(symbol)
                        stack.append(symbol)

        return accessible

    def remove_non_productive_symbols(self) -> "CNFConverter":
        """
        Remove nonterminals that cannot derive terminal strings.

        Returns:
            Self, so pipeline calls can be chained.
        """
        productive = self.compute_productive_nonterminals()

        # Keep the start symbol to preserve grammar shape even if language is empty.
        if self.grammar.start_symbol in self.grammar.nonterminals:
            productive.add(self.grammar.start_symbol)

        new_productions: Dict[Symbol, List[ProductionRHS]] = {}
        for lhs in sorted(productive):
            if lhs not in self.grammar.nonterminals:
                continue

            collected: List[ProductionRHS] = []
            for rhs in self.grammar.productions.get(lhs, []):
                if any(
                    symbol in self.grammar.nonterminals and symbol not in productive
                    for symbol in rhs
                ):
                    continue
                self._add_unique_rhs(collected, rhs)

            if collected:
                new_productions[lhs] = collected

        self.grammar.nonterminals = set(productive) & self.grammar.nonterminals
        self.grammar.productions = new_productions
        self._refresh_terminals_from_productions()
        return self

    def compute_productive_nonterminals(self) -> Set[Symbol]:
        """
        Compute productive nonterminals with fixed-point iteration.
        """
        productive: Set[Symbol] = set()
        changed = True

        while changed:
            changed = False
            for lhs, rhs_list in self.grammar.productions.items():
                if lhs in productive:
                    continue

                for rhs in rhs_list:
                    if all(
                        (symbol not in self.grammar.nonterminals)
                        or (symbol in productive)
                        for symbol in rhs
                    ):
                        productive.add(lhs)
                        changed = True
                        break

        return productive

    def _refresh_terminals_from_productions(self) -> None:
        """
        Keep terminal set consistent with currently retained productions.
        """
        used_terminals: Set[Symbol] = set()
        for rhs_list in self.grammar.productions.values():
            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol not in self.grammar.nonterminals:
                        used_terminals.add(symbol)

        self.grammar.terminals = used_terminals

    def remove_useless_symbols(self) -> "CNFConverter":
        """
        Remove unreachable and non-generating symbols.

        Returns:
            Self, so pipeline calls can be chained.
        """
        return self.remove_non_productive_symbols().remove_inaccessible_symbols()

    def replace_terminals_in_long_rules(self) -> "CNFConverter":
        """
        Replace terminals inside RHS with length > 1 by helper nonterminals.

        Returns:
            Self, so pipeline calls can be chained.
        """
        source_productions: Dict[Symbol, List[ProductionRHS]] = {
            lhs: list(rhs_list) for lhs, rhs_list in self.grammar.productions.items()
        }
        original_nonterminals = set(self.grammar.nonterminals)

        new_productions: Dict[Symbol, List[ProductionRHS]] = {}
        terminal_helpers: Dict[Symbol, Symbol] = {}

        for lhs in sorted(original_nonterminals):
            collected: List[ProductionRHS] = []
            for rhs in source_productions.get(lhs, []):
                if len(rhs) <= 1:
                    self._add_unique_rhs(collected, rhs)
                    continue

                replaced_rhs = list(rhs)
                for idx, symbol in enumerate(rhs):
                    if symbol in self.grammar.terminals:
                        helper = self._get_or_create_terminal_helper(
                            symbol=symbol,
                            terminal_helpers=terminal_helpers,
                            productions=new_productions,
                        )
                        replaced_rhs[idx] = helper

                self._add_unique_rhs(collected, tuple(replaced_rhs))

            if collected:
                new_productions[lhs] = collected

        for terminal, helper in terminal_helpers.items():
            helper_rules = new_productions.setdefault(helper, [])
            self._add_unique_rhs(helper_rules, (terminal,))

        self.grammar.productions = new_productions
        self._refresh_terminals_from_productions()
        return self

    def binarize_long_productions(self) -> "CNFConverter":
        """
        Convert productions with RHS length > 2 into binary productions.

        Returns:
            Self, so pipeline calls can be chained.
        """
        source_productions: Dict[Symbol, List[ProductionRHS]] = {
            lhs: list(rhs_list) for lhs, rhs_list in self.grammar.productions.items()
        }
        original_nonterminals = set(self.grammar.nonterminals)

        new_productions: Dict[Symbol, List[ProductionRHS]] = {}
        suffix_helpers: Dict[Tuple[Symbol, ...], Symbol] = {}

        def ensure_suffix_helper(sequence: Tuple[Symbol, ...]) -> Symbol:
            if sequence in suffix_helpers:
                return suffix_helpers[sequence]

            helper = self._new_nonterminal(prefix="X")
            suffix_helpers[sequence] = helper
            helper_rules = new_productions.setdefault(helper, [])

            if len(sequence) == 2:
                self._add_unique_rhs(helper_rules, sequence)
                return helper

            tail_helper = ensure_suffix_helper(sequence[1:])
            self._add_unique_rhs(helper_rules, (sequence[0], tail_helper))
            return helper

        for lhs in sorted(original_nonterminals):
            collected: List[ProductionRHS] = []
            for rhs in source_productions.get(lhs, []):
                if len(rhs) <= 2:
                    self._add_unique_rhs(collected, rhs)
                    continue

                suffix_helper = ensure_suffix_helper(tuple(rhs[1:]))
                self._add_unique_rhs(collected, (rhs[0], suffix_helper))

            if collected:
                new_productions[lhs] = collected

        self.grammar.productions = new_productions
        self._refresh_terminals_from_productions()
        return self

    def _get_or_create_terminal_helper(
        self,
        *,
        symbol: Symbol,
        terminal_helpers: Dict[Symbol, Symbol],
        productions: Dict[Symbol, List[ProductionRHS]],
    ) -> Symbol:
        """
        Return a reusable helper nonterminal for a terminal symbol.
        """
        if symbol in terminal_helpers:
            return terminal_helpers[symbol]

        base = f"T_{self._sanitize_symbol(symbol)}"
        helper = self._new_nonterminal(prefix=base)
        terminal_helpers[symbol] = helper

        helper_rules = productions.setdefault(helper, [])
        self._add_unique_rhs(helper_rules, (symbol,))
        return helper

    def _new_nonterminal(self, prefix: str) -> Symbol:
        """
        Create a fresh nonterminal name that does not collide with existing ones.
        """
        candidate = prefix
        counter = 1
        while candidate in self.grammar.nonterminals:
            candidate = f"{prefix}_{counter}"
            counter += 1

        self.grammar.nonterminals.add(candidate)
        return candidate

    @staticmethod
    def _sanitize_symbol(symbol: Symbol) -> str:
        """
        Convert arbitrary symbols into safe helper-name fragments.
        """
        cleaned = "".join(ch if ch.isalnum() else "_" for ch in symbol)
        cleaned = cleaned.strip("_")
        return cleaned or "sym"
