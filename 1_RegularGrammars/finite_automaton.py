"""finite_automaton.py
Defines a FiniteAutomaton class for NFA/DFA operations.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Optional, Set, Tuple


class FiniteAutomaton:
    """Represents a finite automaton with Q, Sigma, delta, q0, and F."""

    def __init__(
        self,
        Q: Optional[Set[str]] = None,
        Sigma: Optional[Set[str]] = None,
        delta: Optional[Dict[Tuple[str, str], Set[str]]] = None,
        q0: Optional[str] = None,
        F: Optional[Set[str]] = None,
        **legacy_kwargs,
    ) -> None:
        """Store automaton components and validate the structure.

        The constructor supports both naming styles:
        - Assignment style: Q, Sigma, delta, q0, F
        - Legacy style: states, alphabet, transitions, start_state, accept_states
        """
        if Q is None and "states" in legacy_kwargs:
            Q = legacy_kwargs.pop("states")
        if Sigma is None and "alphabet" in legacy_kwargs:
            Sigma = legacy_kwargs.pop("alphabet")
        if delta is None and "transitions" in legacy_kwargs:
            delta = legacy_kwargs.pop("transitions")
        if q0 is None and "start_state" in legacy_kwargs:
            q0 = legacy_kwargs.pop("start_state")
        if F is None and "accept_states" in legacy_kwargs:
            F = legacy_kwargs.pop("accept_states")

        if legacy_kwargs:
            unknown = ", ".join(sorted(legacy_kwargs.keys()))
            raise TypeError(f"Unexpected constructor arguments: {unknown}")

        if Q is None or Sigma is None or delta is None or q0 is None or F is None:
            raise ValueError("FiniteAutomaton requires Q, Sigma, delta, q0, and F.")

        self.Q = set(Q)
        self.Sigma = set(Sigma)
        normalized_delta = {}
        for (state, symbol), next_states in delta.items():
            if isinstance(next_states, str):
                normalized_delta[(state, symbol)] = {next_states}
            else:
                normalized_delta[(state, symbol)] = set(next_states)
        self.delta = normalized_delta
        self.q0 = q0
        self.F = set(F)

        # Backward-compatible aliases.
        self.states = self.Q
        self.alphabet = self.Sigma
        self.transitions = self.delta
        self.start_state = self.q0
        self.accept_states = self.F

        self._validate()

    def _validate(self) -> None:
        """Check that states, alphabet, and transitions are internally consistent."""
        if self.q0 not in self.Q:
            raise ValueError("Start state must belong to the automaton state set.")

        if not self.F.issubset(self.Q):
            raise ValueError("Accept states must be a subset of automaton states.")

        for (state, symbol), next_states in self.delta.items():
            if state not in self.Q:
                raise ValueError(f"Transition uses unknown state: {state}")
            if symbol not in self.Sigma:
                raise ValueError(f"Transition uses symbol not in alphabet: {symbol}")
            if not next_states.issubset(self.Q):
                raise ValueError(
                    f"Transition from ({state}, {symbol}) points to unknown states."
                )

    def is_deterministic(self) -> bool:
        """Return True when every transition leads to at most one next state."""
        return all(len(next_states) <= 1 for next_states in self.delta.values())

    def _move(self, current_states: Set[str], symbol: str) -> Set[str]:
        """Compute reachable states after reading one symbol from current states."""
        next_states = set()
        for state in current_states:
            next_states.update(self.delta.get((state, symbol), set()))
        return next_states

    def string_belongs_to_language(self, input_string: str) -> bool:
        """Simulate transitions on input_string and return True if it is accepted."""
        current_states = {self.q0}

        for symbol in input_string:
            # Symbols outside Sigma are rejected immediately.
            if symbol not in self.Sigma:
                return False

            # For NFA support, track all reachable states after each symbol.
            current_states = self._move(current_states, symbol)
            if not current_states:
                return False

        return any(state in self.F for state in current_states)

    def accepts(self, input_string: str) -> bool:
        """Check whether the automaton accepts the provided input string."""
        return self.string_belongs_to_language(input_string)

    def to_dfa(self) -> "FiniteAutomaton":
        """Convert this automaton to an equivalent DFA using subset construction."""
        start_subset = frozenset([self.q0])
        queue = deque([start_subset])
        visited = {start_subset}

        subset_to_name = {start_subset: self._subset_name(start_subset)}
        dfa_states = {subset_to_name[start_subset]}
        dfa_transitions = {}
        dfa_accept_states = set()

        while queue:
            subset = queue.popleft()
            subset_name = subset_to_name[subset]

            if any(state in self.F for state in subset):
                dfa_accept_states.add(subset_name)

            for symbol in sorted(self.Sigma):
                next_subset = set()
                for state in subset:
                    next_subset.update(self.delta.get((state, symbol), set()))
                next_subset = frozenset(next_subset)

                if next_subset not in subset_to_name:
                    subset_to_name[next_subset] = self._subset_name(next_subset)

                next_name = subset_to_name[next_subset]
                dfa_transitions[(subset_name, symbol)] = {next_name}
                dfa_states.add(next_name)

                if next_subset not in visited:
                    visited.add(next_subset)
                    queue.append(next_subset)

        return FiniteAutomaton(
            Q=dfa_states,
            Sigma=set(self.Sigma),
            delta=dfa_transitions,
            q0=subset_to_name[start_subset],
            F=dfa_accept_states,
        )

    @staticmethod
    def _subset_name(subset: frozenset[str]) -> str:
        """Build a readable state name for a DFA subset state."""
        if not subset:
            return "{}"
        return "{" + ",".join(sorted(subset)) + "}"

    @classmethod
    def from_grammar(cls, grammar: "Grammar") -> "FiniteAutomaton":
        """Create an automaton from a right-linear grammar."""
        return grammar.to_finite_automaton()

    def __str__(self) -> str:
        """Return a readable multi-line representation of the automaton."""
        lines = ["Finite Automaton:"]
        lines.append(f"  Q (states): {sorted(self.Q)}")
        lines.append(f"  Sigma (alphabet): {sorted(self.Sigma)}")
        lines.append(f"  q0 (start): {self.q0}")
        lines.append(f"  F (accepting): {sorted(self.F)}")
        lines.append("  Transitions:")

        for (state, symbol), next_states in sorted(self.delta.items()):
            lines.append(f"    delta({state}, {symbol}) -> {sorted(next_states)}")

        return "\n".join(lines)
