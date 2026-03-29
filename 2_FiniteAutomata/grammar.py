from __future__ import annotations


class Grammar:
    """Core formal grammar model with explicit production storage."""

    def __init__(
        self,
        nonterminals: set[str],
        terminals: set[str],
        productions: dict[str, set[tuple[str, ...]]] | None,
        start_symbol: str,
    ) -> None:
        self.nonterminals = self._validate_string_set(
            "nonterminals", nonterminals, allow_empty=False
        )
        self.terminals = self._validate_string_set("terminals", terminals, allow_empty=True)

        if self.nonterminals.intersection(self.terminals):
            raise ValueError("nonterminals and terminals must be disjoint sets.")

        if not isinstance(start_symbol, str):
            raise TypeError("start_symbol must be a string.")
        if start_symbol not in self.nonterminals:
            raise ValueError("start_symbol must belong to nonterminals.")
        self.start_symbol = start_symbol

        if productions is None:
            productions = {}
        if not isinstance(productions, dict):
            raise TypeError("productions must be a dict[str, set[tuple[str, ...]]].")

        self.productions: dict[str, set[tuple[str, ...]]] = {}
        for lhs, rhs_set in productions.items():
            if lhs not in self.nonterminals:
                raise ValueError(f"Production LHS must be a nonterminal: {lhs!r}.")
            validated_rhs_set = self._validate_rhs_set(rhs_set)
            self.productions[lhs] = set(validated_rhs_set)

    def add_production(self, lhs: str, rhs_tuple: tuple[str, ...]) -> None:
        """Add one production rule: lhs -> rhs_tuple."""
        if lhs not in self.nonterminals:
            raise ValueError(f"LHS must be a nonterminal: {lhs!r}.")
        validated_rhs = self._validate_rhs(rhs_tuple)
        self.productions.setdefault(lhs, set()).add(validated_rhs)

    def classify_chomsky(self) -> str:
        """
        Classify grammar in the Chomsky hierarchy.

        Returns one of: Type-3, Type-2, Type-1, Type-0.
        """
        # We test from most restrictive to least restrictive.
        if self._is_type_3_right_linear():
            return "Type-3"
        if self._is_type_2_context_free():
            return "Type-2"
        if self._is_type_1_context_sensitive():
            return "Type-1"
        return "Type-0"

    def pretty_print(self) -> str:
        """Return a human-readable multiline representation."""
        return str(self)

    def __str__(self) -> str:
        lines = [
            "Grammar(",
            f"  nonterminals={self._format_set(self.nonterminals)},",
            f"  terminals={self._format_set(self.terminals)},",
            f"  start_symbol={self.start_symbol!r},",
            "  productions={",
        ]

        if self.productions:
            for lhs in sorted(self.productions):
                rhs_parts = []
                for rhs in sorted(self.productions[lhs], key=lambda item: (len(item), item)):
                    rhs_parts.append(" ".join(rhs) if rhs else "epsilon")
                lines.append(f"    {lhs!r}: {' | '.join(rhs_parts)},")
        else:
            lines.append("    # no productions")

        lines.append("  }")
        lines.append(")")
        return "\n".join(lines)

    def _validate_rhs_set(self, rhs_set: object) -> set[tuple[str, ...]]:
        if not isinstance(rhs_set, set):
            raise TypeError("Each productions[lhs] value must be a set[tuple[str, ...]].")
        validated: set[tuple[str, ...]] = set()
        for rhs in rhs_set:
            validated.add(self._validate_rhs(rhs))
        return validated

    def _validate_rhs(self, rhs: object) -> tuple[str, ...]:
        if not isinstance(rhs, tuple):
            raise TypeError("Each RHS must be a tuple[str, ...].")
        if any(not isinstance(symbol, str) for symbol in rhs):
            raise TypeError("Each RHS symbol must be a string.")

        allowed_symbols = self.nonterminals.union(self.terminals)
        invalid = [symbol for symbol in rhs if symbol not in allowed_symbols]
        if invalid:
            raise ValueError(
                f"RHS contains symbols outside nonterminals/terminals: {invalid!r}."
            )
        return tuple(rhs)

    def _is_type_3_right_linear(self) -> bool:
        """
        Type-3 check with right-linear-only policy:
        A -> aB | a | epsilon
        """
        for lhs, rhs_set in self.productions.items():
            # Type-3 still requires a single nonterminal on the LHS.
            if lhs not in self.nonterminals:
                return False

            for rhs in rhs_set:
                # Per requested Type-3 rule, A -> epsilon is allowed.
                if len(rhs) == 0:
                    continue

                # A -> a
                if len(rhs) == 1 and rhs[0] in self.terminals:
                    continue

                # A -> aB (right-linear form).
                if (
                    len(rhs) == 2
                    and rhs[0] in self.terminals
                    and rhs[1] in self.nonterminals
                ):
                    continue

                # Any other shape is not right-linear.
                # This also rejects left-linear rules like A -> Ba, so we never mix forms.
                return False

        return True

    def _is_type_2_context_free(self) -> bool:
        # Context-free requires exactly one nonterminal on the LHS.
        return all(lhs in self.nonterminals for lhs in self.productions)

    def _is_type_1_context_sensitive(self) -> bool:
        # For the optional S -> epsilon exception, also require S not to appear on any RHS.
        start_symbol_appears_on_rhs = any(
            self.start_symbol in rhs
            for rhs_set in self.productions.values()
            for rhs in rhs_set
        )

        for lhs, rhs_set in self.productions.items():
            # LHS must contain at least one nonterminal (single-symbol LHS in this model).
            if lhs not in self.nonterminals:
                return False

            lhs_len = 1
            for rhs in rhs_set:
                rhs_len = len(rhs)

                if rhs_len == 0:
                    if lhs == self.start_symbol and not start_symbol_appears_on_rhs:
                        continue
                    return False

                # Non-contracting rule: |LHS| <= |RHS|
                if lhs_len > rhs_len:
                    return False

        return True

    @staticmethod
    def _validate_string_set(
        field_name: str, value: object, allow_empty: bool
    ) -> set[str]:
        if not isinstance(value, set):
            raise TypeError(f"{field_name} must be a set[str].")
        if not allow_empty and not value:
            raise ValueError(f"{field_name} cannot be empty.")
        if any(not isinstance(item, str) for item in value):
            raise TypeError(f"{field_name} must contain only strings.")
        return set(value)

    @staticmethod
    def _format_set(values: set[str]) -> str:
        return "{" + ", ".join(repr(item) for item in sorted(values)) + "}"
