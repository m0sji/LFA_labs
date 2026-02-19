from finite_automaton import build_variant_18_nfa


def main() -> None:
    automaton = build_variant_18_nfa()
    print("Variant 18 NFA:")
    print(automaton.pretty_print())
    is_det = automaton.is_deterministic()
    print(f"Deterministic: {is_det}")
    assert is_det is False, "Variant 18 must be non-deterministic."

    dfa = automaton.to_dfa()
    print("\nDFA from subset construction (without dead state):")
    print(dfa.pretty_print())
    print(f"DFA states: {sorted(dfa.states)}")
    print("DFA transitions:")
    for (from_state, symbol), to_states in sorted(
        dfa.transitions.items(), key=lambda item: (item[0][0], item[0][1])
    ):
        to_state = next(iter(to_states))
        print(f"  delta({from_state}, {symbol}) = {to_state}")

    grammar = automaton.to_regular_grammar()
    print("\nRegular grammar generated from Variant 18 FA:")
    print(grammar.pretty_print())
    grammar_type = grammar.classify_chomsky()
    print(f"Chomsky classification: {grammar_type}")
    assert grammar_type == "Type-3", "Variant 18 generated grammar should be Type-3."


if __name__ == "__main__":
    main()
