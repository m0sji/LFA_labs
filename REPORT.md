# Context-Free Grammar to Chomsky Normal Form Converter (Variant 18)

### Course: Formal Languages & Finite Automata
### Author: Oberst Eduard FAF-243

----

## Theory
In Formal Languages, a context-free grammar (CFG) is defined as a 4-tuple:
`G = (V_N, V_T, P, S)`, where:
- `V_N` is the set of nonterminal symbols
- `V_T` is the set of terminal symbols
- `P` is the set of productions
- `S` is the start symbol

Chomsky Normal Form (CNF) is a restricted form of CFG where every production has only one of the following forms:
- `A -> BC` (both `B` and `C` are nonterminals)
- `A -> a` (a single terminal)

To transform a general CFG into CNF, several normalization steps are required:
1. Eliminate epsilon productions (`A -> epsilon`) except possibly for the start symbol.
2. Eliminate unit productions (`A -> B`).
3. Eliminate useless symbols:
   - non-productive symbols (cannot derive terminal strings)
   - inaccessible symbols (cannot be reached from start symbol)
4. Replace terminals in long mixed productions with helper nonterminals.
5. Split long productions into binary productions.

The implemented project follows exactly this pipeline and keeps every algorithm generic, so the converter works for any grammar represented in the same data model.


## Objectives:

* Design a reusable OOP model for context-free grammars in Python.
* Implement grammar parsing from Python dictionaries and pretty-printing.
* Implement epsilon-production elimination with nullable-symbol analysis.
* Implement unit-production elimination using unit-pair closure.
* Implement non-productive and inaccessible symbol elimination.
* Implement final CNF normalization:
  - terminal replacement in long rules
  - binarization of long right-hand sides
* Ensure duplicate productions are avoided in every stage.
* Provide a command-line flow that prints the grammar after each transformation.
* Add automated `unittest` coverage for core conversion properties.


## Implementation description

### 1) Project architecture
The project is structured as a small Python package:
- `src/cfg_cnf/grammar.py` for the grammar data model
- `src/cfg_cnf/cnf_converter.py` for all transformations
- `examples/sample_grammar.py` for Variant 18 grammar fixture
- `main.py` for CLI execution
- `tests/test_cnf_converter.py` for unit tests

This separation keeps data modeling, transformation logic, executable flow, and validation independent and easy to maintain.

### 2) Grammar class (`Grammar`)
`Grammar` stores `nonterminals`, `terminals`, `productions`, and `start_symbol`.  
Internally, each right-hand side is stored as a tuple of symbols, and epsilon is represented as an empty tuple.

Implemented utility features:
- `from_dict(...)` to build a grammar from Python structures
- `add_production(...)` with duplicate-checking
- `pretty()` for deterministic, human-readable output
- compact RHS tokenization (`aB`) and spaced RHS tokenization (`a B`)

### 3) Epsilon-production elimination
First, nullable symbols are computed by fixed-point iteration:
- direct nullable: if `A -> epsilon`
- indirect nullable: if all symbols in an RHS are nullable

Then for every production, all combinations of nullable-symbol removals are generated, excluding empty RHS except where the start symbol is nullable.
This preserves language behavior as much as possible while removing epsilon rules.

```python
def find_nullable_symbols(self) -> Set[Symbol]:
    nullable: Set[Symbol] = set()
    changed = True
    while changed:
        changed = False
        for lhs, rhs_list in self.grammar.productions.items():
            if lhs in nullable:
                continue
            for rhs in rhs_list:
                if not rhs or all(symbol in nullable for symbol in rhs):
                    nullable.add(lhs)
                    changed = True
                    break
    return nullable
```

### 4) Unit-production elimination
Unit pairs `(A, B)` are computed with graph reachability, where edges represent unit productions (`A -> B`).
For each source nonterminal `A`, all non-unit productions of all reachable `B` are copied into `A`.
As a result, direct and indirect unit rules are eliminated.

Key effect for Variant 18:
- `S -> B` is removed
- `S` inherits `B` productions (`S -> a`, `S -> bS`)

```python
def _is_unit_production(self, rhs: ProductionRHS) -> bool:
    return len(rhs) == 1 and rhs[0] in self.grammar.nonterminals
```

### 5) Useless-symbol elimination
Two passes are implemented:
1. `remove_non_productive_symbols()`: keeps only nonterminals that can derive terminal strings.
2. `remove_inaccessible_symbols()`: keeps only nonterminals reachable from `S`.

After each pass:
- productions are filtered
- symbol sets are updated
- terminals are refreshed from remaining productions

In Variant 18, `C` is removed as inaccessible after previous simplification steps.

### 6) Final CNF transformation
#### 6.1 Replace terminals in long rules
If a production has length greater than 1 and contains terminals, each terminal is replaced by a helper nonterminal (`T_a`, `T_b`, etc.).
Helpers are reused through a dictionary map, so the same terminal does not create multiple helper symbols.

#### 6.2 Binarize long rules
If a production has length greater than 2, it is decomposed into binary rules using helper symbols (`X`, `X_1`, ...).
A suffix-helper cache is used to reuse equivalent decomposition fragments.

```python
if len(rhs) <= 2:
    self._add_unique_rhs(collected, rhs)
else:
    suffix_helper = ensure_suffix_helper(tuple(rhs[1:]))
    self._add_unique_rhs(collected, (rhs[0], suffix_helper))
```

### 7) Command-line flow
`main()` builds Variant 18 grammar and prints the grammar after every stage:
1. Initial grammar
2. After epsilon elimination
3. After unit elimination
4. After non-productive elimination
5. After inaccessible elimination
6. After terminal replacement
7. Final CNF grammar

This makes the transformation process transparent and easy to verify during demonstrations.

### 8) Testing strategy (`unittest`)
Implemented tests:
- `test_nullable_detection` checks nullable set correctness
- `test_unit_production_removal` verifies `S -> B` elimination and no unit rules remain
- `test_inaccessible_symbol_elimination` checks removal of inaccessible `C`
- `test_final_cnf_shape_validation` checks that every rule is either:
  - length 1 with terminal RHS, or
  - length 2 with nonterminal RHS

All tests pass with:
`python -m unittest discover -s tests -v`

### 9) Complexity and correctness notes
To keep the converter reliable, I maintained a few invariants in every stage:
- each production list contains unique RHS alternatives only;
- nonterminal/terminal sets are updated after structural deletions;
- the final grammar is validated against CNF shape constraints.

Approximate computational behavior:
- nullable/productive/accessibility detection is fixed-point based and repeatedly scans productions;
- unit elimination is graph reachability over nonterminal unit edges;
- epsilon elimination may generate combinational variants for RHS with multiple nullable symbols;
- terminal replacement and binarization are mostly linear in the number of produced symbols, plus helper creation.

For this lab size, runtime is effectively instant, but these notes explain where growth appears on larger grammars.

* Code snippets from your files.

```python
def main() -> None:
    converter = CNFConverter(build_sample_grammar())
    _print_stage("Initial Grammar", converter)
    converter.remove_epsilon_productions()
    _print_stage("After Epsilon-Production Elimination", converter)
    converter.remove_unit_productions()
    _print_stage("After Unit-Production Elimination", converter)
    converter.remove_non_productive_symbols()
    _print_stage("After Non-Productive Symbol Elimination", converter)
    converter.remove_inaccessible_symbols()
    _print_stage("After Inaccessible Symbol Elimination", converter)
    converter.replace_terminals_in_long_rules()
    _print_stage("After Terminal Replacement in Long Rules", converter)
    converter.binarize_long_productions()
    _print_stage("Final CNF Grammar", converter)
```

* If needed, screenshots.

Instead of screenshots, terminal output snapshots were captured directly in text form for reproducibility.


## Personal Experience
This lab went well from the architecture point of view because the work was split early into two clean classes (`Grammar` and `CNFConverter`). That decision reduced complexity later, especially when adding many independent transformation steps and tests.  

What went good:
- The OOP design made incremental implementation straightforward. Each new method (`remove_epsilon_productions`, `remove_unit_productions`, etc.) fit naturally in `CNFConverter` without refactoring previous code.
- The pipeline approach made debugging easier because each stage could be printed independently in `main()`.
- The test-first mindset for critical behaviors (nullable set, unit elimination, CNF shape) prevented regressions while extending the converter.
- Reuse maps for helper symbols (`T_a`, `T_b`, cached suffix helpers) kept the grammar compact and avoided symbol explosion.

What went bad / difficult:
- Handling epsilon in Windows terminal output caused encoding issues, so output had to normalize `epsilon` during display.
- Preventing duplicates at every stage required careful repeated checks; missing one deduplication point quickly produced noisy grammars.
- Unit and epsilon elimination interact in subtle ways, so running steps in wrong order caused incorrect intermediate grammars during early iterations.
- Keeping terminal/nonterminal sets consistent after deletions was easy to overlook; without refreshing symbol sets, later checks could become invalid.

What I learned:
- Correctness in grammar normalization depends more on invariants than on raw code volume.
- Fixed-point algorithms are natural and reliable for nullable/productive computations.
- Small helper methods and strict data normalization (tuple RHS) drastically simplify later transformations and testing.
- Having stage-by-stage outputs is not just for presentation; it is a practical debugging tool in formal-language tasks.

How I would improve this further:
- Add property-based tests for random small grammars.
- Add optional graph visualization for accessibility and unit-pair relations.
- Add deterministic ordering options for all production lists to improve diff readability.
- Extend tests with edge cases where start symbol derives epsilon.
- Add benchmark tests on larger synthetic grammars to measure scaling.
- Add CLI flags to execute only selected phases during debugging.


## Conclusions 
The laboratory objective was achieved: a complete Python project now converts Variant 18 CFG into CNF through all required stages and validates the behavior with automated tests.

Final CNF grammar produced by the implemented converter:

```text
V_N = {A, B, D, S, T_a, T_b, X}
V_T = {a, b}
Start = S
Productions:
S -> a | T_b S | T_a B | T_b A | b
A -> b | T_a D | AS | T_b X | T_b B | a | T_b S | T_a B | T_b A
B -> a | T_b S
D -> BB
T_a -> a
T_b -> b
X -> AB
```

Test results summary:
- `4` tests executed
- all tests passed
- CNF shape validation succeeded for all productions generated by `to_cnf()`

Reproducibility commands:

```bash
python main.py
python -m unittest discover -s tests -v
```

Final reflection: the strongest part of this lab was the transparent step-by-step pipeline.  
Each transformation is visible, testable, and independently debuggable, which is exactly what formal-language tooling needs.


## References
1. John E. Hopcroft, Rajeev Motwani, Jeffrey D. Ullman, *Introduction to Automata Theory, Languages, and Computation*.
2. Michael Sipser, *Introduction to the Theory of Computation*.
3. Course materials for Formal Languages & Finite Automata.
4. Python Documentation - `dataclasses`, `typing`, `unittest`:
   https://docs.python.org/3/library/
