from __future__ import annotations

from grammar import Grammar


class FiniteAutomaton:
    """Core finite automaton model (supports NFA-style transitions)."""

    def __init__(
        self,
        states: set[str],
        alphabet: set[str],
        start_state: str,
        final_states: set[str],
        transitions: dict[tuple[str, str], set[str]] | None = None,
    ) -> None:
        self.states = self._validate_string_set("states", states, allow_empty=False)
        self.alphabet = self._validate_string_set("alphabet", alphabet, allow_empty=True)

        if not isinstance(start_state, str):
            raise TypeError("start_state must be a string.")
        if start_state not in self.states:
            raise ValueError("start_state must belong to states.")
        self.start_state = start_state

        self.final_states = self._validate_string_set(
            "final_states", final_states, allow_empty=True
        )
        if not self.final_states.issubset(self.states):
            raise ValueError("final_states must be a subset of states.")

        if transitions is None:
            transitions = {}
        if not isinstance(transitions, dict):
            raise TypeError("transitions must be a dict[(state, symbol), set[state]].")

        self.transitions: dict[tuple[str, str], set[str]] = {}
        for key, to_states in transitions.items():
            if (
                not isinstance(key, tuple)
                or len(key) != 2
                or not isinstance(key[0], str)
                or not isinstance(key[1], str)
            ):
                raise TypeError(
                    "Each transition key must be a tuple[str, str]: (from_state, symbol)."
                )

            from_state, symbol = key
            if from_state not in self.states:
                raise ValueError(f"Transition from unknown state: {from_state!r}.")
            if symbol not in self.alphabet:
                raise ValueError(f"Transition uses symbol not in alphabet: {symbol!r}.")

            validated_targets = self._validate_string_set(
                "transition target set", to_states, allow_empty=False
            )
            if not validated_targets.issubset(self.states):
                raise ValueError(
                    "Transition target states must all belong to states."
                )

            # Store a defensive copy to keep internal state isolated.
            self.transitions[(from_state, symbol)] = set(validated_targets)

    def add_transition(self, from_state: str, symbol: str, to_state: str) -> None:
        """Add one transition: (from_state, symbol) -> to_state."""
        if from_state not in self.states:
            raise ValueError(f"Unknown from_state: {from_state!r}.")
        if symbol not in self.alphabet:
            raise ValueError(f"Symbol {symbol!r} is not in alphabet.")
        if to_state not in self.states:
            raise ValueError(f"Unknown to_state: {to_state!r}.")

        self.transitions.setdefault((from_state, symbol), set()).add(to_state)

    def is_deterministic(self) -> bool:
        """Return True iff each (state, symbol) has at most one target and no epsilon edges."""
        epsilon_symbols = {"", "eps", "epsilon"}
        for (_, symbol), to_states in self.transitions.items():
            if symbol in epsilon_symbols:
                return False
            if len(to_states) > 1:
                return False
        return True

    def to_dfa(self) -> "FiniteAutomaton":
        """
        Convert this NFA to a DFA using subset construction.

        Internal DFA states are represented as frozenset[str].
        Design choice: transitions to the empty set are omitted, so no dead state is created.
        """
        start_subset = frozenset({self.start_state})
        discovered: set[frozenset[str]] = {start_subset}
        queue: list[frozenset[str]] = [start_subset]

        subset_transitions: dict[tuple[frozenset[str], str], frozenset[str]] = {}

        while queue:
            current_subset = queue.pop(0)
            for symbol in sorted(self.alphabet):
                next_states: set[str] = set()
                for state in current_subset:
                    next_states.update(self.transitions.get((state, symbol), set()))

                # Intentionally omit empty-set moves; this DFA has no explicit dead state.
                if not next_states:
                    continue

                next_subset = frozenset(next_states)
                subset_transitions[(current_subset, symbol)] = next_subset

                if next_subset not in discovered:
                    discovered.add(next_subset)
                    queue.append(next_subset)

        def subset_name(subset: frozenset[str]) -> str:
            return "{" + ",".join(sorted(subset)) + "}"

        dfa_states = {subset_name(subset) for subset in discovered}
        dfa_start_state = subset_name(start_subset)
        dfa_final_states = {
            subset_name(subset)
            for subset in discovered
            if any(state in self.final_states for state in subset)
        }

        dfa_transitions: dict[tuple[str, str], set[str]] = {}
        for (from_subset, symbol), to_subset in subset_transitions.items():
            from_name = subset_name(from_subset)
            to_name = subset_name(to_subset)
            dfa_transitions[(from_name, symbol)] = {to_name}

        return FiniteAutomaton(
            states=dfa_states,
            alphabet=set(self.alphabet),
            start_state=dfa_start_state,
            final_states=dfa_final_states,
            transitions=dfa_transitions,
        )

    def to_regular_grammar(self) -> Grammar:
        """
        Convert this finite automaton to a right-linear regular grammar.

        Mapping used:
        - each FA state name is reused as a grammar nonterminal
        - each transition q_i --a--> q_j becomes q_i -> a q_j
        - each final state q_f gets epsilon production q_f -> epsilon
          (encoded as an empty RHS tuple: ()).
        """
        productions: dict[str, set[tuple[str, ...]]] = {
            state: set() for state in self.states
        }

        for (from_state, symbol), to_states in self.transitions.items():
            for to_state in to_states:
                productions[from_state].add((symbol, to_state))

        for final_state in self.final_states:
            productions[final_state].add(())

        return Grammar(
            nonterminals=set(self.states),
            terminals=set(self.alphabet),
            productions=productions,
            start_symbol=self.start_state,
        )

    def to_dot(self) -> str:
        """
        Export automaton as Graphviz DOT text.

        - directed graph
        - explicit start arrow
        - double-circle final states
        - one edge per transition target (supports NFA multi-target transitions)
        """
        start_node_id = "__start__"

        def q(text: str) -> str:
            return f'"{self._dot_escape(text)}"'

        lines = [
            "digraph FiniteAutomaton {",
            "  rankdir=LR;",
            "  node [shape=circle];",
            f"  {q(start_node_id)} [shape=point];",
            f"  {q(start_node_id)} -> {q(self.start_state)};",
        ]

        for state in sorted(self.states):
            shape = "doublecircle" if state in self.final_states else "circle"
            lines.append(f"  {q(state)} [shape={shape}];")

        for (from_state, symbol), to_states in sorted(
            self.transitions.items(), key=lambda item: (item[0][0], item[0][1])
        ):
            # Emit one edge per target so NFA branching remains explicit.
            for to_state in sorted(to_states):
                lines.append(
                    f"  {q(from_state)} -> {q(to_state)} [label={q(symbol)}];"
                )

        lines.append("}")
        return "\n".join(lines)

    def pretty_print(self) -> str:
        """Return a human-readable multiline representation."""
        return str(self)

    def __str__(self) -> str:
        lines = [
            "FiniteAutomaton(",
            f"  states={self._format_set(self.states)},",
            f"  alphabet={self._format_set(self.alphabet)},",
            f"  start_state={self.start_state!r},",
            f"  final_states={self._format_set(self.final_states)},",
            "  transitions={",
        ]

        if self.transitions:
            for (from_state, symbol), to_states in sorted(
                self.transitions.items(), key=lambda item: (item[0][0], item[0][1])
            ):
                lines.append(
                    "    "
                    f"({from_state!r}, {symbol!r}): {self._format_set(to_states)},"
                )
        else:
            lines.append("    # no transitions")

        lines.append("  }")
        lines.append(")")
        return "\n".join(lines)

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

    @staticmethod
    def _dot_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')


def build_variant_18_nfa() -> FiniteAutomaton:
    """Build the Variant 18 NFA from the lab statement."""
    automaton = FiniteAutomaton(
        states={"q0", "q1", "q2", "q3"},
        alphabet={"a", "b", "c"},
        start_state="q0",
        final_states={"q3"},
        transitions={},
    )

    automaton.add_transition("q0", "a", "q0")
    automaton.add_transition("q0", "a", "q1")
    automaton.add_transition("q1", "b", "q2")
    automaton.add_transition("q2", "a", "q2")
    automaton.add_transition("q2", "b", "q3")
    automaton.add_transition("q3", "a", "q3")

    # Symbol 'c' intentionally has no outgoing transitions in this variant.
    return automaton
