from __future__ import annotations

from pathlib import Path
import sys


# Allow imports from the existing lab folder while keeping root-level execution:
#   python main.py
LAB_DIR = Path(__file__).resolve().parent / "1_RegularGrammars"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from finite_automaton import build_variant_18_nfa


def _format_productions(grammar) -> list[str]:
    lines: list[str] = []
    for lhs in sorted(grammar.productions):
        rhs_texts: list[str] = []
        for rhs in sorted(grammar.productions[lhs], key=lambda item: (len(item), item)):
            rhs_texts.append(" ".join(rhs) if rhs else "epsilon")
        lines.append(f"{lhs} -> {' | '.join(rhs_texts)}")
    return lines


def main() -> None:
    # 1) Build Variant 18 NFA
    nfa = build_variant_18_nfa()
    print("1) Built Variant 18 NFA")

    # 2) Print whether it is deterministic
    print(f"2) Deterministic: {nfa.is_deterministic()}")

    # 3) Convert it to regular grammar
    grammar = nfa.to_regular_grammar()
    print("3) Converted NFA to regular grammar")

    # 4) Print grammar productions
    print("4) Grammar productions:")
    for production in _format_productions(grammar):
        print(f"   {production}")

    # 5) Print Chomsky type
    chomsky_type = grammar.classify_chomsky()
    print(f"5) Chomsky type: {chomsky_type}")

    # 6) Convert NFA to DFA
    dfa = nfa.to_dfa()
    print("6) Converted NFA to DFA")

    # 7) Print DFA states and transitions
    print("7) DFA states and transitions:")
    print(f"   states: {sorted(dfa.states)}")
    print(f"   start: {dfa.start_state}")
    print(f"   finals: {sorted(dfa.final_states)}")
    print("   transitions:")
    if dfa.transitions:
        for (from_state, symbol), to_states in sorted(
            dfa.transitions.items(), key=lambda item: (item[0][0], item[0][1])
        ):
            to_state = next(iter(to_states))
            print(f"     delta({from_state}, {symbol}) = {to_state}")
    else:
        print("     (none)")

    # Optional DOT export for both automata.
    print("8) NFA DOT:")
    print(nfa.to_dot())
    print("9) DFA DOT:")
    print(dfa.to_dot())


if __name__ == "__main__":
    main()
