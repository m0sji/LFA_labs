# Laboratory Work: Lexer/Scanner for a Mini Programming Language

### Course: Formal Languages & Finite Automata
### Author: OBERST EDUARD FAF-243

----

## Theory
A lexer (scanner) is the first stage of translation in a compiler/interpreter. It transforms a raw character stream into a stream of tokens that are easier for a parser to process.  
In formal language terms, lexical analysis corresponds to recognizing patterns from regular languages (identifiers, numbers, operators, delimiters), which can be modeled with finite automata.  
In this laboratory work, the scanner is implemented manually in Python and keeps positional metadata (`line`, `column`) for each token, enabling precise diagnostics for syntax and semantic stages.  
The lexer must also ignore irrelevant input for parsing, such as whitespace and comments, while still advancing position counters correctly.


## Objectives:

* Design and implement a lexer for a mini programming language in Python 3.10+.
* Build a complete `TokenType` enumeration for literals, operators, keywords, delimiters, and EOF.
* Implement a `Token` dataclass that stores token category, value, line, and column.
* Recognize integer and floating-point numeric literals.
* Recognize string literals enclosed in double quotes and support common escapes.
* Recognize arithmetic operators: `+`, `-`, `*`, `/`, `^`.
* Recognize comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`.
* Recognize assignment operator: `=`.
* Recognize logical/control keywords: `if`, `else`, `while`, `let`.
* Recognize trigonometric functions as reserved words: `sin`, `cos`, `tan`.
* Recognize boolean literals: `true`, `false`.
* Recognize identifiers with letters/underscore followed by alphanumerics/underscore.
* Recognize grouping symbols: `(`, `)`, `[`, `]`.
* Skip single-line comments introduced by `//`.
* Skip whitespace/newlines while preserving accurate line and column counters.
* Raise `LexerError` with location for invalid characters or malformed lexemes.
* Provide a runnable demo (`main.py`) and automated tests (`pytest`) for valid/invalid inputs.


## Implementation description

* The implementation is split into four files:
  `token.py` (token model), `lexer.py` (scanner logic), `main.py` (demo), `test_lexer.py` (unit tests).
* `token.py` contains `TokenType` and `Token`. Since the lab asked for the filename `token.py`, compatibility exports for Python's own `token` module are included to avoid import conflicts in standard-library internals.
* `lexer.py` contains:
  `LexerError` for structured lexical exceptions and `Lexer` for scanning logic.
* `Lexer.__init__` initializes source text, cursor index, line/column counters, and token output list.
* `Lexer.tokenize()` performs a left-to-right scan:
  first skips whitespace/comments, then dispatches by current character type (digit, quote, alphabetic/underscore, operator/delimiter).
* Numeric scanning:
  `_scan_number()` first consumes digits for integer part, optionally consumes `.` plus digits for float part, then emits `INTEGER` or `FLOAT`.
* String scanning:
  `_scan_string()` consumes opening quote, reads until closing quote, handles escape sequences (`\"`, `\\`, `\n`, `\t`, `\r`), and raises error on newline/EOF before closing quote.
* Identifier/keyword scanning:
  `_scan_identifier_or_keyword()` consumes `[A-Za-z_][A-Za-z0-9_]*` and maps lexeme through keyword table.  
  If lexeme is `true`/`false`, token value is stored as Python boolean (`True`/`False`).
* Operator scanning:
  `match/case` handles single-character tokens (`+`, `-`, `*`, `/`, `^`, parentheses, brackets).  
  Dedicated helper methods process multi-character operators: `==`, `!=`, `<=`, `>=`.
* Comment handling:
  `_skip_whitespace_and_comments()` consumes spaces/tabs/newlines and ignores text from `//` to end-of-line.
* Position tracking:
  `_advance()` updates line/column for every consumed character; on newline it increments `line` and resets `column` to `1`.
* Complexity:
  The lexer is linear in source length, `O(n)`, because each character is consumed at most a constant number of times.
* Validation:
  `main.py` demonstrates token stream output in format
  `TokenType.NAME | value | line:col`.  
  `test_lexer.py` checks valid tokenization, comments/strings/positions, invalid character handling, and unterminated strings.


* Code snippets.

```python
# token.py (fragment)
from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENTIFIER = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    LET = auto()
    TRUE = auto()
    FALSE = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    EQ_EQ = auto()
    BANG_EQ = auto()
    LT = auto()
    GT = auto()
    LT_EQ = auto()
    GT_EQ = auto()
    ASSIGN = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    EOF = auto()

@dataclass(slots=True)
class Token:
    type: TokenType
    value: object
    line: int
    column: int
```

```python
# lexer.py (fragment from tokenize)
def tokenize(self) -> list[Token]:
    while not self._is_at_end():
        self._skip_whitespace_and_comments()
        if self._is_at_end():
            break

        ch = self._current_char()
        if ch.isdigit():
            self._scan_number()
            continue
        if ch == '"':
            self._scan_string()
            continue
        if ch.isalpha() or ch == "_":
            self._scan_identifier_or_keyword()
            continue

        start_line, start_column = self.line, self.column
        match ch:
            case "+":
                self._advance()
                self._add_token(TokenType.PLUS, "+", start_line, start_column)
            case "=":
                self._scan_equals_related()
            case "!":
                self._scan_bang_related()
            case _:
                raise LexerError(f"Unrecognized character {ch!r}", start_line, start_column)
```

```python
# main.py (fragment)
lexer = Lexer(sample_source)
tokens = lexer.tokenize()
for token in tokens:
    print(f"TokenType.{token.type.name:<10} | {token.value!s:<16} | {token.line}:{token.column}")
```




## Personal Experience
What went well:
* The modular structure (`token.py`, `lexer.py`, `main.py`, tests) made implementation clearer and easier to debug.
* Using helper methods for each lexeme class reduced complexity in `tokenize()`.
* Line/column tracking was useful immediately during debugging because errors were easy to localize.
* `match/case` in Python 3.10+ made operator handling cleaner than long chained `if/elif`.

What was difficult:
* A practical issue appeared because naming the file `token.py` can shadow Python's standard `token` module.
* String literal handling required careful treatment of escapes and unterminated strings.
* Multi-character operators (`==`, `!=`, `<=`, `>=`) needed exact lookahead logic to avoid wrong token splits.
* Test execution depended on local environment configuration (`pytest` installation).

How the problems were solved:
* The `token.py` file was adapted to remain compatible with standard-library imports.
* Dedicated helper methods (`_scan_string`, `_scan_equals_related`, `_scan_bang_related`, etc.) were used to isolate edge cases.
* Error handling was centralized through `LexerError` messages that include line and column.

What I learned:
* Even a simple lexer requires careful state management and clear token boundaries.
* Good diagnostics are as important as correct token recognition.
* Lexing tasks map naturally to finite-automata thinking from FLFA theory.


## Conclusions 
The implemented scanner satisfies the laboratory requirements and successfully tokenizes a mini language with numeric literals, strings, identifiers, keywords, arithmetic/comparison operators, trigonometric functions, booleans, brackets/parentheses, comments, and EOF.  
The lexer provides precise position-aware errors (`line`, `column`) for invalid input, which is critical for later parser stages.  
From a software-engineering perspective, decomposition into focused helper methods improved maintainability and testability.  
Overall, the project demonstrates how formal-language concepts (regular structures and deterministic scanning) are applied in a practical Python implementation.


## References
* Formal Languages & Finite Automata course materials (lecture and lab notes).
* Python 3 documentation, lexical conventions and exceptions.
* `pytest` documentation for unit testing in Python projects.
