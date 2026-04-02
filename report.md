# Dynamic Regular Expression String Generator

### Course: Formal Languages & Finite Automata
### Author: Oberst Eduard

---

## 1. Objective

The objective of this assignment is to design and implement a Python program (`regex_generator.py`) that:

- parses regular expressions dynamically (not hardcoded per pattern),
- builds an internal structural representation (Abstract Syntax Tree, AST),
- and generates random strings that are valid with respect to each expression.

The implementation targets the following expressions:

1. `(a|b)(c|d)E+G?`
2. `P(Q|R|S)T(UV|W|X)*Z+`
3. `1(0|1)*2(3|4)^536`, interpreted as `1(0|1)*2(3|4)^5 36`

---

## 2. Theory of Regular Expressions

Regular expressions describe formal languages by using operators over symbols:

- **Concatenation** combines expressions sequentially (e.g., `ab`).
- **Alternation** (`|`) expresses choice (e.g., `a|b`).
- **Grouping** (`(...)`) controls structure and precedence.
- Repetition operator `*` means zero or more.
- Repetition operator `+` means one or more.
- Repetition operator `?` means optional (zero or one).
- Repetition operator `^n` means exactly `n` repetitions (for this project).

From a formal-languages perspective, regular expressions define regular languages, equivalent in expressive power to finite automata.

---

## 3. Applications of Regular Expressions

Regular expressions are widely used in both theory and practice:

- lexical analysis and tokenization in compilers,
- validation of structured input (identifiers, IDs, constrained formats),
- search/filter operations in text processing,
- extraction pipelines in data engineering,
- specification of accepted patterns in protocol and parser front ends.

In this assignment, regexes are not only matched but also used *constructively* to generate valid strings.

---

## 4. Description of the Given Regexes

### Regex 1: `(a|b)(c|d)E+G?`

- First symbol: either `a` or `b`.
- Second symbol: either `c` or `d`.
- Then one to five `E` (program-limited `+` behavior).
- Optional `G`.

Example valid strings: `acEG`, `bdEEE`, `bcEEEG`.

### Regex 2: `P(Q|R|S)T(UV|W|X)*Z+`

- Starts with `P`.
- Then one of `Q`, `R`, `S`.
- Then `T`.
- Then zero to five repetitions of one block from `{UV, W, X}`.
- Ends with one to five `Z`.

Example valid strings: `PQTUVUVZ`, `PRTXZ`, `PSTWUVZZ`.

### Regex 3: `1(0|1)*2(3|4)^536`

Required interpretation:

`1(0|1)*2(3|4)^5 36`

This means:

- start with `1`,
- then zero to five bits from `{0,1}`,
- then `2`,
- then exactly five symbols from `{3,4}`,
- then literal `3` and literal `6`.

Example valid strings: `1023333336`, `124443336`, `110012343436`.

---

## 5. Algorithm Explanation

The solution follows a standard compiler-style pipeline:

1. **Tokenization**  
   Convert the regex text into a token stream (`LPAREN`, `ALT`, `STAR`, `LITERAL`, etc.).

2. **Parsing**  
   Use recursive-descent parsing with precedence rules to transform tokens into an AST.

3. **Generation**  
   Recursively traverse the AST and produce strings. Alternation picks one branch randomly, concatenation joins child results in order, and repetition expands child nodes according to operator limits.

4. **Validation (sanity check)**  
   Convert AST back to a bounded Python regex and verify generated strings match.

This architecture is dynamic: the same logic handles any expression in the supported grammar.

---

## 6. Parser and AST

### Precedence Handling

The parser enforces operator precedence correctly:

1. quantifiers (`*`, `+`, `?`, `^n`) bind to the nearest preceding primary,
2. concatenation is next,
3. alternation (`|`) is lowest.

### Group Parsing

Grouped expressions such as `(UV|W|X)` are parsed as:

- one `Alternate` node,
- containing option `Concat([Literal('U'), Literal('V')])`,
- containing option `Literal('W')`,
- containing option `Literal('X')`.

### AST Node Types

- `Literal`
- `Concat`
- `Alternate`
- `Repeat`

This representation is minimal but sufficient for both generation and tracing.

---

## 7. Generator Logic

Generation is AST-driven:

- `Literal` returns one symbol.
- `Concat` concatenates generated outputs from all children.
- `Alternate` selects one option with uniform randomness.
- `Repeat` samples repetition count in a configured range and expands child generation that many times.

Because generation uses the parsed structure, behavior is data-driven and independent of specific hardcoded regexes.

---

## 8. Repetition Limits

To keep output finite and practical, repetition operators are bounded:

- `*` -> `0..5`
- `+` -> `1..5`
- `?` -> `0..1`
- `^n` -> exactly `n`

For `^n`, the assignment-specific behavior is preserved so `^536` is interpreted as `^5` followed by literals `3` and `6`.

---

## 9. Bonus: Step-by-Step Trace Function

The function `generate_with_steps(...)` records every generation decision:

- which alternative branch was selected,
- how many repetitions were chosen,
- intermediate concatenation results,
- final output.

This trace is useful for debugging, teaching, and demonstrating correctness of derivation.

---

## 10. Example Outputs

Example outputs produced by the program (seeded run, 10 per regex):

### For `(a|b)(c|d)E+G?`

- `adEEEEE`
- `adEEEEEG`
- `bcE`
- `adEG`
- `bdEEEG`

### For `P(Q|R|S)T(UV|W|X)*Z+`

- `PQTUVUVXZZZ`
- `PRTXXZ`
- `PSTWWUVWXZZZ`
- `PRTXUVZZZ`
- `PSTZ`

### For `1(0|1)*2(3|4)^5 36`

- `10024433336`
- `11023334436`
- `1010123434436`
- `123334336`
- `1024334336`

Mandatory sample-like examples also valid:

- `acEG`
- `PQTUVUVZ`
- `1023333336`

---

## 11. Difficulties

The main implementation difficulties were:

- **Disambiguating `^n`** in the third regex while preserving assignment interpretation.
- **Enforcing precedence** cleanly in a compact recursive-descent parser.
- **Representing grouped alternations** like `(UV|W|X)` without ad-hoc conditions.
- **Maintaining dynamic behavior** while adding validation and trace functionality.

These issues were resolved by a strict tokenizer/parser separation and explicit AST node semantics.

---

## 12. Conclusion

The assignment goals were achieved through a modular architecture:

- tokenizer,
- precedence-aware parser,
- AST-based random generator,
- trace and validation utilities.

The result demonstrates how formal regex definitions can be converted into executable generators. The implementation is extensible and can serve as a foundation for future work (e.g., character classes, escaped symbols, or direct automaton construction).

---

## 13. Personal Experience

### What went well

- The compiler-like pipeline (tokenizer -> parser -> AST -> generator) worked well and kept the code organized.
- AST design simplified both generation and explanation.
- The trace function gave immediate visibility into generation decisions and helped verify correctness.

### What went poorly

- The `^n` interpretation in `^536` was initially ambiguous and required careful handling to match assignment constraints.
- Early versions were correct functionally but less rigorous in validation and reporting.

### What was learned

- Precedence rules are the most important part of parser reliability.
- Even for small grammars, a clear AST model improves maintainability significantly.
- Bounded repetition is a practical compromise between formal meaning and finite test output.

### What can be improved next

- Add richer grammar support (`[]`, escapes, ranges, and escaped metacharacters).
- Improve distribution control for generation (weighted branching/repetition).
- Add automated unit tests for tokenization, parse trees, and generation validity.

---

## References

1. Course materials: *Formal Languages & Finite Automata*.
2. Hopcroft, J. E., Motwani, R., Ullman, J. D. *Introduction to Automata Theory, Languages, and Computation*.
3. Python documentation (`re` module) for validation methodology.
