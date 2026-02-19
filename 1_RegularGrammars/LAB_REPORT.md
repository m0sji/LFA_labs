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

For this specific grammar (variant 18), the recursive parts can be read as cycles:

* `S -> aA -> abS` generates the block `ab`
* `S -> aB -> aC -> aabS` generates the block `aab`
* `S -> aB -> aC -> aaa` is the terminating branch

So the language can be described as:

* `L = (ab | aab)* aaa`

A finite automaton is defined as a 5-tuple `FA = (Q, Sigma, delta, q0, F)`:

* `Q` is the set of states.
* `Sigma` is the input alphabet.
* `delta` is the transition function.
* `q0` is the start state.
* `F` is the set of accepting states.

An input string belongs to the language if, after processing all symbols, at least one reached state is accepting.

Because state `S` has two transitions on symbol `a` (`S -> A` and `S -> B`), the converted automaton is an NFA. The implementation keeps a set of current states at each step, which is the standard NFA simulation method.

## Objectives:

* Implement a `Grammar` class for a right-linear grammar using `VN`, `VT`, `P`, and `S`.
* Implement random string derivation with `generate_string()` and helper `generate_5_strings()`.
* Convert the grammar to a `FiniteAutomaton` with fields `Q`, `Sigma`, `delta`, `q0`, and `F`.
* Implement FA membership checking with `string_belongs_to_language(input_string)`.
* Demonstrate the implementation on variant 18 and print Boolean membership results.
* Validate grammar and automaton definitions to reject invalid symbols or malformed rules.
* Explain NFA behavior for nondeterministic transitions and acceptance.
* Analyze practical limits (random generation loops, edge-case strings, and invalid input symbols).

## Implementation description

The grammar for variant 18 is:

* `S -> aA | aB`
* `A -> bS`
* `B -> aC`
* `C -> a | bS`

Implementation is split into three files with clear responsibilities:

* `grammar.py` handles grammar storage, validation, random derivation, and grammar-to-FA conversion.
* `finite_automaton.py` handles FA validation, NFA simulation, determinism checks, and subset construction (`to_dfa`).
* `main.py` builds variant 18, runs demo generation, and prints membership checks for representative test strings.

`Grammar.__init__()` and `FiniteAutomaton.__init__()` also support legacy argument names and normalize internal structures. This keeps the code backward-compatible while preserving strict validation.

`Grammar.generate_string()` starts from `S`, repeatedly finds the leftmost non-terminal, chooses one production with `random.choice`, replaces it, and stops when only terminals remain. The method uses a maximum step limit to prevent infinite derivations.

`Grammar.to_finite_automaton()` applies standard right-linear conversion:

* For `X -> aY`, add transition `delta[(X, 'a')] -> Y`.
* For `X -> a`, add transition `delta[(X, 'a')] -> F` (special final state).
* For `X -> e`, mark `X` as accepting.

`FiniteAutomaton.string_belongs_to_language()` simulates transitions symbol by symbol and returns `True` if an accepting state is reachable at the end of the input.

Complexity notes:

* String generation is bounded by `max_steps`, so it is guaranteed to terminate with success or a clear runtime error.
* Membership checking is linear in input length and tracks a set of states each step (`O(|input| * |Q|)` in the NFA case).

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

```python
# NFA simulation idea in finite_automaton.py
current_states = {self.q0}
for symbol in input_string:
    if symbol not in self.Sigma:
        return False
    current_states = self._move(current_states, symbol)
return any(state in self.F for state in current_states)
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

Additional interpretation:

* Accepted examples (`aaa`, `abaaa`, `aabaaa`) all fit the pattern `(ab | aab)* aaa`.
* Rejected examples fail for structural reasons:
  * `aa` is too short and does not reach the terminal branch ending in `aaa`.
  * `abba` does not match the cycle pattern before termination.
  * `b` and `''` cannot be generated because derivations from `S` always start with `a`.

Limitations and possible extensions:

* Generated strings are random and can repeat; uniqueness filtering could improve demonstration quality.
* There is no seed parameter exposed in `main.py`, so runs are not reproducible by default.
* The report currently includes textual output only; adding automaton diagrams would improve readability.
* Unit tests for validation errors and conversion correctness would strengthen confidence in edge cases.

## Personal Experience

This laboratory work was useful because it connected theory directly with runnable code.

What went well:

* Defining the grammar components (`VN`, `VT`, `P`, `S`) was straightforward.
* Converting right-linear productions to FA transitions was clear and systematic.
* The generated strings and membership checks matched, which confirmed the logic.
* Splitting logic by file (`grammar.py`, `finite_automaton.py`, `main.py`) made debugging easier.

What did not work well at first:

* Random derivation can loop too long when recursion repeats, so generation needed a step limit.
* Handling terminal-only productions (`X -> a`) required adding a dedicated final FA state; without this, acceptance was incorrect.
* Nondeterministic transitions needed set-based state tracking; using a single current state would miss valid paths.
* At first it was easy to overlook invalid input symbols; explicit alphabet checks were necessary.

What I improved / learned:

* I now better understand why right-linear grammars map naturally to finite automata.
* I learned to validate grammar behavior by testing both generated strings and manual edge cases.
* I improved implementation reliability by adding safeguards and clearer transition handling.
* I learned to reason about the language structure directly from production cycles, not only from code output.

## References

* Laboratory course notes for Formal Languages and Finite Automata.
* Project source files: `1_RegularGrammars/grammar.py`, `1_RegularGrammars/finite_automaton.py`, `1_RegularGrammars/main.py`.
