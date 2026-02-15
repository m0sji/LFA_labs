"""grammar.py
Defines a Grammar class for basic right-linear grammar operations.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Set


class Grammar:
    """Represents a right-linear grammar with VN, VT, P, and start symbol S."""

    def __init__(
        self,
        VN: Optional[Set[str]] = None,
        VT: Optional[Set[str]] = None,
        P: Optional[Dict[str, List[str]]] = None,
        S: Optional[str] = None,
        **legacy_kwargs,
    ) -> None:
        """Store grammar components and validate their consistency.

        The constructor supports both naming styles:
        - Assignment style: VN, VT, P, S
        - Legacy style: non_terminals, terminals, productions, start_symbol
        """
        if VN is None and "non_terminals" in legacy_kwargs:
            VN = legacy_kwargs.pop("non_terminals")
        if VT is None and "terminals" in legacy_kwargs:
            VT = legacy_kwargs.pop("terminals")
        if P is None and "productions" in legacy_kwargs:
            P = legacy_kwargs.pop("productions")
        if S is None and "start_symbol" in legacy_kwargs:
            S = legacy_kwargs.pop("start_symbol")

        if legacy_kwargs:
            unknown = ", ".join(sorted(legacy_kwargs.keys()))
            raise TypeError(f"Unexpected constructor arguments: {unknown}")

        if VN is None or VT is None or P is None or S is None:
            raise ValueError("Grammar requires VN, VT, P, and S.")

        self.VN = set(VN)
        self.VT = set(VT)
        self.P = {left: list(rights) for left, rights in P.items()}
        self.S = S

        # Backward-compatible aliases used by existing demo code.
        self.non_terminals = self.VN
        self.terminals = self.VT
        self.productions = self.P
        self.start_symbol = self.S

        self._validate()

    def _validate(self) -> None:
        """Check that grammar symbols and productions follow right-linear rules."""
        if self.S not in self.VN:
            raise ValueError("The start symbol must be a non-terminal.")

        if not self.VN:
            raise ValueError("The grammar must contain at least one non-terminal.")

        if not self.VT:
            raise ValueError("The grammar must contain at least one terminal.")

        for left, rights in self.P.items():
            if left not in self.VN:
                raise ValueError(f"Invalid production left side: {left}")

            if not rights:
                raise ValueError(f"Production list for {left} cannot be empty.")

            for right in rights:
                if right == "e":
                    continue

                if len(right) == 1:
                    if right not in self.VT:
                        raise ValueError(f"Invalid terminal production: {left} -> {right}")
                    continue

                if len(right) == 2:
                    symbol, next_non_terminal = right[0], right[1]
                    if symbol not in self.VT or next_non_terminal not in self.VN:
                        raise ValueError(f"Invalid right-linear production: {left} -> {right}")
                    continue

                raise ValueError(
                    "Only right-linear productions are supported: A->aB, A->a, or A->e."
                )

    def _contains_non_terminal(self, sentential_form: str) -> bool:
        """Return True when any non-terminal symbol exists in the current string."""
        return any(symbol in self.VN for symbol in sentential_form)

    def generate_string(self, max_steps: int = 25) -> str:
        """Generate one terminal string by randomly applying grammar productions."""
        current = self.S

        for _ in range(max_steps):
            # Stop when no non-terminals remain in the sentential form.
            if not self._contains_non_terminal(current):
                return current

            # Expand the leftmost non-terminal.
            replace_index = -1
            replace_symbol = ""
            for index, symbol in enumerate(current):
                if symbol in self.VN:
                    replace_index = index
                    replace_symbol = symbol
                    break

            if replace_index == -1:
                return current

            options = self.P.get(replace_symbol, [])
            if not options:
                raise RuntimeError(f"No productions available for non-terminal: {replace_symbol}")

            chosen = random.choice(options)
            replacement = "" if chosen == "e" else chosen
            current = current[:replace_index] + replacement + current[replace_index + 1 :]

        raise RuntimeError(
            "Maximum derivation steps reached before obtaining a terminal-only string."
        )

    def generate_5_strings(self, max_steps: int = 25) -> List[str]:
        """Generate five terminal strings using repeated random derivations."""
        generated = []
        for _ in range(5):
            generated.append(self.generate_string(max_steps=max_steps))
        return generated

    def to_finite_automaton(self) -> "FiniteAutomaton":
        """Convert this right-linear grammar into an equivalent finite automaton."""
        from finite_automaton import FiniteAutomaton

        final_state = "F"
        states = set(self.VN)
        states.add(final_state)

        transitions = {}
        accept_states = {final_state}

        for left, rights in self.P.items():
            for right in rights:
                if right == "e":
                    accept_states.add(left)
                    continue

                if len(right) == 1:
                    key = (left, right)
                    transitions.setdefault(key, set()).add(final_state)
                else:
                    symbol, next_state = right[0], right[1]
                    key = (left, symbol)
                    transitions.setdefault(key, set()).add(next_state)

        return FiniteAutomaton(
            Q=states,
            Sigma=set(self.VT),
            delta=transitions,
            q0=self.S,
            F=accept_states,
        )

    def __str__(self) -> str:
        """Return a readable multi-line representation of the grammar."""
        lines = ["Grammar:"]
        lines.append(f"  VN (non-terminals): {sorted(self.VN)}")
        lines.append(f"  VT (terminals): {sorted(self.VT)}")
        lines.append(f"  S (start symbol): {self.S}")
        lines.append("  P (productions):")
        for left in sorted(self.P):
            right_side = " | ".join(self.P[left])
            lines.append(f"    {left} -> {right_side}")
        return "\n".join(lines)
