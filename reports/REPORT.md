# Parser & Building an Abstract Syntax Tree

### Course: Formal Languages & Finite Automata
### Author: OBERST Eduard FAF-243

----

## Theory

Parsing is the process of taking a sequence of tokens and checking whether that sequence follows a formal grammar.  
If the input is valid, the parser builds a structured representation of the program.

In this laboratory work, lexical analysis and syntax analysis are separated into clear stages:

1. **Lexical analysis (Lexer)** converts source text into tokens such as identifiers, integers, operators, and punctuation.
2. **Syntax analysis (Parser)** consumes those tokens according to grammar rules.
3. **AST construction** produces a tree representation that is easier to analyze, transform, or evaluate later.

An **Abstract Syntax Tree (AST)** is a simplified tree form of a program.  
It keeps the syntactic structure (for example operator hierarchy), but removes unnecessary surface details such as spaces and formatting.

This project is implemented in **Python 3.11+** using only the standard library.

## Objectives

* Design a tiny language that supports assignments, arithmetic expressions, parentheses, and multiple statements separated by semicolons.
* Implement a lexical analyzer using **regular expressions**.
* Represent token categories using a **`TokenType` enum**.
* Define clean AST node classes with Python dataclasses.
* Implement a **handwritten recursive descent parser** with operator precedence handling.
* Print the AST in a readable hierarchical format.
* Validate the implementation with unit tests.

## Implementation Description

The implementation is modular and organized by responsibility:

* `src/lexer` contains token definitions and regex-based lexical analysis.
* `src/parser` contains AST node classes and recursive descent parser logic.
* `src/main.py` demonstrates a complete run: read input, tokenize, parse, and print AST.
* `tests` contains short unit tests for lexer and parser behavior.

### Project Structure and Design Decisions

The project follows a layered design, where each layer has a single responsibility:

1. **Lexical layer**: receives raw text and outputs typed tokens.
2. **Syntactic layer**: receives tokens and outputs AST nodes.
3. **Presentation layer**: prints tokens and AST in readable form for demonstration.

This separation is useful for maintenance and evaluation in a laboratory context:

* A lexer change (for example, adding a new token) does not require rewriting parser internals.
* Parser logic can be tested independently with prepared token streams.
* AST printing remains independent from parsing rules, which makes debugging clearer.

The implementation intentionally avoids external dependencies and parser generators to keep all algorithms explicit and educational.

### Lexical Analysis

The lexer scans text from left to right using compiled regular expressions.  
Each match is mapped to a `TokenType` value and converted into a `Token` object.

Key points:

* Whitespace is recognized and skipped.
* Integers store numeric value in `literal`.
* Invalid characters produce a clear `LexerError` with line and column.

Short excerpt:

```python
TOKEN_PATTERNS = [
    ("WHITESPACE", r"[ \t\r\n\f\v]+"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("INTEGER", r"\d+"),
    ("ASSIGN", r"="),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("SEMICOLON", r";"),
]
```

How tokenization works step by step:

1. Start at the current position in the source text.
2. Try to match the master regex pattern.
3. If no rule matches, raise `LexerError` with exact line/column.
4. If whitespace matches, update position counters and skip.
5. Otherwise, create a `Token` and append it to the token list.
6. After the input ends, append an explicit `EOF` token.

The explicit `EOF` token simplifies parser logic because parsing can always rely on a known terminal symbol at the end of the stream.

### Syntax Analysis and AST Building

The parser is a handwritten recursive descent parser.  
It uses methods that directly reflect grammar non-terminals:

* `parse()`
* `parse_statement_list()`
* `parse_statement()`
* `parse_assignment()`
* `parse_expression()`
* `parse_term()`
* `parse_factor()`
* `eat(expected_type)`

The parser constructs AST dataclass nodes (`Program`, `Assignment`, `BinaryOperation`, `Number`, `Identifier`) while consuming tokens.

### Data Structures Used

The following data structures are central to the project:

* **Enum (`TokenType`)**: provides fixed token categories and prevents string-based mistakes.
* **Dataclass (`Token`)**: stores lexical category, raw text, optional numeric value, and source position.
* **Dataclass AST nodes**: provide compact and readable syntax tree representation.
* **List of tokens**: parser input sequence with O(1) indexed access by current position.

These choices keep the code short and readable while still being robust enough for syntax analysis tasks.

### AST Printing

A dedicated function `pretty_print_ast()` prints the tree hierarchically, making parent-child relations explicit and easy to inspect during debugging.

## Grammar

The language grammar used in the parser is:

```ebnf
program         -> statement_list EOF
statement_list  -> statement (';' statement)* ';'?
statement       -> assignment | expression
assignment      -> IDENTIFIER '=' expression
expression      -> term (('+' | '-') term)*
term            -> factor (('*' | '/') factor)*
factor          -> INTEGER | IDENTIFIER | '(' expression ')'
```

This grammar is intentionally simple and suitable for recursive descent parsing.

### Notes About Grammar Design

The grammar was chosen to be:

* **LL-friendly**: compatible with top-down recursive descent parsing.
* **Minimal**: only essential constructs for the assignment.
* **Deterministic**: precedence is encoded in rule hierarchy, reducing ambiguity.

One practical detail is the distinction between:

* `assignment` (starts with identifier followed by `=`), and
* `expression` (may also start with identifier).

This is handled in the parser with a one-token lookahead strategy.

## Token Types

Token categories are defined with a `TokenType` enum:

* `IDENTIFIER`
* `INTEGER`
* `ASSIGN`
* `PLUS`
* `MINUS`
* `MUL`
* `DIV`
* `LPAREN`
* `RPAREN`
* `SEMICOLON`
* `EOF`

Each recognized token is stored in a `Token` dataclass with:

* `token_type`
* `lexeme`
* `literal`
* `line`
* `column`

## AST Structure

Core AST node classes:

* `ASTNode`: base class.
* `Program`: root node containing statement list.
* `Assignment`: variable assignment (`name = expression`).
* `BinaryOperation`: arithmetic operation with `left`, `operator`, and `right`.
* `Number`: integer literal.
* `Identifier`: variable reference.

Example conceptual tree:

```text
Program
  Assignment
    Identifier(x)
    BinaryOperation(+)
      Number(3)
      BinaryOperation(*)
        Number(4)
        Number(2)
```

## Parser Explanation

Operator precedence is handled by splitting expression parsing into levels:

1. `parse_expression()` handles `+` and `-` (lower precedence).
2. `parse_term()` handles `*` and `/` (higher precedence).
3. `parse_factor()` handles atomic elements: numbers, identifiers, parenthesized expressions.

Because `parse_expression()` calls `parse_term()` first, multiplication and division are grouped before addition and subtraction.  
Parentheses work by recursively calling `parse_expression()` inside `(` and `)`.

This design avoids ambiguity and keeps the code educational.

### Parser Control Flow

`parse()` is the entry point and executes this flow:

1. Parse a statement list.
2. Check that no unexpected tokens remain.
3. Consume `EOF`.
4. Return `Program(statements=[...])`.

Error handling is centralized via clear exceptions:

* `eat(expected_type)` validates token expectations.
* `ParserError` includes token type and source position.
* Errors are propagated to `main.py`, where they are printed cleanly.

This approach provides useful diagnostics while keeping the parser implementation simple.

## Results / Example Run

Sample input program:

```text
x = 5 + 2 * (3 - 1);
y = x / 2;
z = y + 7;
```

Example token output (shortened):

```text
IDENTIFIER('x') ASSIGN INTEGER('5') PLUS INTEGER('2') MUL LPAREN ...
... RPAREN SEMICOLON IDENTIFIER('y') ASSIGN IDENTIFIER('x') DIV INTEGER('2') ...
```

Example AST output:

```text
Program
  Assignment
    Identifier(x)
    BinaryOperation(+)
      Number(5)
      BinaryOperation(*)
        Number(2)
        BinaryOperation(-)
          Number(3)
          Number(1)
  Assignment
    Identifier(y)
    BinaryOperation(/)
      Identifier(x)
      Number(2)
```

All unit tests pass:

* Lexer tests: identifiers, integers, operators/punctuation, invalid character errors.
* Parser tests: assignment correctness, precedence, parentheses effect, multiple statements.

### Additional Example (Precedence Check)

Input:

```text
x = 2 + 3 * 4;
```

Expected AST idea:

```text
Assignment
  Identifier(x)
  BinaryOperation(+)
    Number(2)
    BinaryOperation(*)
      Number(3)
      Number(4)
```

This confirms that multiplication is grouped before addition.

### Additional Example (Parentheses Check)

Input:

```text
x = (2 + 3) * 4;
```

Expected AST idea:

```text
Assignment
  Identifier(x)
  BinaryOperation(*)
    BinaryOperation(+)
      Number(2)
      Number(3)
    Number(4)
```

This confirms that parentheses override default precedence.

## Personal Experience

This laboratory was useful for understanding how source code is transformed step by step.

What went well:

* Defining `TokenType` first made the rest of the implementation clearer.
* Using regular expressions simplified token recognition and made the lexer concise.
* Dataclass-based AST nodes gave readable debug output with minimal code.
* The recursive descent approach matched the grammar naturally.

What was difficult:

* Correct line/column tracking required careful handling of whitespace and newlines.
* Distinguishing assignment statements from expression statements required lookahead logic.
* Ensuring precedence was represented correctly in the AST required focused testing.

Challenges encountered:

* Keeping the parser simple while still producing clear syntax errors.
* Designing tests that are short but still cover key behaviors.
* Maintaining consistency between token names, grammar rules, parser logic, and AST node types.

Overall, the challenges were manageable and helped build a better understanding of practical compiler front-end design.

### What I Would Improve Next Time

If I continue this project, I would improve:

* **Error recovery**: continue parsing after a syntax error to report multiple issues in one run.
* **Language features**: add unary operators in grammar and AST consistently for all paths.
* **Semantic phase**: add a symbol table and checks for undefined identifiers.
* **Evaluator**: execute parsed statements to validate AST correctness functionally.
* **Test breadth**: add edge-case tests (very long identifiers, malformed parentheses sequences, empty statements).

## Conclusion

The project successfully implements a complete mini parsing pipeline in Python:

* regex-based lexical analysis,
* token categorization via `TokenType` enum,
* handwritten recursive descent parsing,
* AST construction and pretty-printing,
* unit testing for core correctness.

The final result is clean, modular, and suitable for a student laboratory submission.  
It also provides a strong base for future extensions such as unary operators, evaluation, semantic checks, or code generation.

In addition, the project demonstrates good software engineering practice for small language tools:

* separation of concerns,
* deterministic grammar-to-code mapping,
* test-driven validation of critical parser behavior,
* readable diagnostics for educational use.

## References

1. Aho, A. V., Lam, M. S., Sethi, R., Ullman, J. D. *Compilers: Principles, Techniques, and Tools* (2nd Edition), Pearson.
2. Python Software Foundation. *Python 3 Documentation*.
3. Python Software Foundation. `re` module documentation: <https://docs.python.org/3/library/re.html>
4. Python Software Foundation. `dataclasses` documentation: <https://docs.python.org/3/library/dataclasses.html>
