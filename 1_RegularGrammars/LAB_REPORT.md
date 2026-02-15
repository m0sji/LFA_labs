# Laboratory Work 1: Right-Linear Grammar and Finite Automaton (Variant 18)

### Course: Formal Languages & Finite Automata
### Author: Oberst Eduard

----

## Theory
In this laboratory work, two core concepts are used: formal grammar and finite automaton.

A formal grammar is defined as a 4-tuple `G = (VN, VT, P, S)`:

* `VN` is the set of non-terminal symbols.
* `VT` is the set of terminal symbols.
* `P` is the set of production rules.
* `S` is the start symbol.

The implemented grammar is right-linear, so each production has one of these forms:

* `X -> aY`
* `X -> a`
* `X -> e`

Because it is right-linear, the generated language is regular.

A finite automaton is defined as a 5-tuple `FA = (Q, Sigma, delta, q0, F)`:

* `Q` is the set of states.
* `Sigma` is the input alphabet.
* `delta` is the transition function.
* `q0` is the start state.
* `F` is the set of accepting states.

An input string belongs to the language if, after processing all symbols, at least one reached state is accepting.

## Objectives:

* Implement a `Grammar` class for a right-linear grammar using `VN`, `VT`, `P`, and `S`.
* Implement random string derivation with `generate_string()` and helper `generate_5_strings()`.
* Convert the grammar to a `FiniteAutomaton` with fields `Q`, `Sigma`, `delta`, `q0`, and `F`.
* Implement FA membership checking with `string_belongs_to_language(input_string)`.
* Demonstrate the implementation on variant 18 and print Boolean membership results.

## Implementation description

The grammar for variant 18 is:

* `S -> aA | aB`
* `A -> bS`
* `B -> aC`
* `C -> a | bS`

`Grammar.generate_string()` starts from `S`, repeatedly finds the leftmost non-terminal, chooses one production with `random.choice`, replaces it, and stops when only terminals remain. The method uses a maximum step limit to prevent infinite derivations.

`Grammar.to_finite_automaton()` applies standard right-linear conversion:

* For `X -> aY`, add transition `delta[(X, 'a')] -> Y`.
* For `X -> a`, add transition `delta[(X, 'a')] -> F` (special final state).
* For `X -> e`, mark `X` as accepting.

`FiniteAutomaton.string_belongs_to_language()` simulates transitions symbol by symbol and returns `True` if an accepting state is reachable at the end of the input.

Code snippets from the implementation:

```python
# Variant 18 grammar in main.py
productions = {
    "S": ["aA", "aB"],
    "A": ["bS"],
    "B": ["aC"],
    "C": ["a", "bS"],
}
```

```python
# Core idea of generate_string in grammar.py
current = self.S
while contains_non_terminal(current):
    X = leftmost_non_terminal(current)
    replacement = random.choice(self.P[X])
    current = replace_leftmost(current, X, replacement)
return current
```

```python
# Conversion rule example in to_finite_automaton (grammar.py)
if len(right) == 2:         # X -> aY
    delta[(X, a)].add(Y)
else:                       # X -> a
    delta[(X, a)].add("F")
```

## Conclusions / Screenshots / Results

Example run output (`python main.py`):

Generated strings:

* `abaaa`
* `abababaababababaaa`
* `abaaa`
* `aaa`
* `aabababaababaabababaabababaaa`

Membership test results:

* `'aaa' -> True`
* `'abaaa' -> True`
* `'aabaaa' -> True`
* `'aa' -> False`
* `'abba' -> False`
* `'b' -> False`
* `'' -> False`

The results confirm that the grammar generation and FA membership simulation are consistent with each other.

## References

* Laboratory course notes for Formal Languages and Finite Automata.
* Project source files: `formal_languages_project/grammar.py`, `formal_languages_project/finite_automaton.py`, `formal_languages_project/main.py`.
