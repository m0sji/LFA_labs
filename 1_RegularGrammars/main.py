"""main.py
Demo runner for the formal languages assignment project.
"""

from grammar import Grammar


def build_variant_18_grammar() -> Grammar:
    """Build grammar for variant 18: S->aA|aB, A->bS, B->aC, C->a|bS."""
    non_terminals = {"S", "A", "B", "C"}
    terminals = {"a", "b"}

    productions = {
        "S": ["aA", "aB"],
        "A": ["bS"],
        "B": ["aC"],
        "C": ["a", "bS"],
    }

    return Grammar(
        VN=non_terminals,
        VT=terminals,
        P=productions,
        S="S",
    )


def main() -> None:
    """Run variant 18 demo: generation, conversion to FA, and membership tests."""
    grammar = build_variant_18_grammar()
    automaton = grammar.to_finite_automaton()

    print("Variant 18 grammar:")
    print("S -> aA | aB")
    print("A -> bS")
    print("B -> aC")
    print("C -> a | bS")
    print()

    print("5 generated strings:")
    for index, generated in enumerate(grammar.generate_5_strings(max_steps=100), start=1):
        print(f"  {index}. {generated}")

    print()
    test_strings = ["aaa", "abaaa", "aabaaa", "aa", "abba", "b", ""]
    print("Membership test results:")
    for word in test_strings:
        result = automaton.string_belongs_to_language(word)
        print(f"  {word!r} -> {result}")


if __name__ == "__main__":
    main()
