"""Unit tests for CFG to CNF conversion steps."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


# Make `src/` importable when tests run from project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cfg_cnf import CNFConverter  # noqa: E402
from examples.sample_grammar import build_sample_grammar  # noqa: E402


class CNFConverterTests(unittest.TestCase):
    """Validate key conversion stages for Variant 18 grammar."""

    def test_nullable_detection(self) -> None:
        """Nullable symbols should be detected with fixed-point logic."""
        grammar = build_sample_grammar()
        converter = CNFConverter(grammar)

        nullable = converter.find_nullable_symbols()
        self.assertEqual(nullable, {"A"})

    def test_unit_production_removal(self) -> None:
        """Unit productions must be removed and replaced by inherited rules."""
        grammar = build_sample_grammar()
        converter = CNFConverter(grammar)

        converter.remove_unit_productions()

        # S -> B must be eliminated.
        self.assertNotIn(("B",), grammar.productions.get("S", []))
        # S should inherit non-unit productions from B.
        self.assertIn(("a",), grammar.productions.get("S", []))
        self.assertIn(("b", "S"), grammar.productions.get("S", []))

        # No unit productions should remain.
        for rhs_list in grammar.productions.values():
            for rhs in rhs_list:
                self.assertFalse(len(rhs) == 1 and rhs[0] in grammar.nonterminals)

    def test_inaccessible_symbol_elimination(self) -> None:
        """Unreachable nonterminals (like C) should be removed."""
        grammar = build_sample_grammar()
        converter = CNFConverter(grammar)

        converter.remove_epsilon_productions()
        converter.remove_unit_productions()
        converter.remove_inaccessible_symbols()

        self.assertNotIn("C", grammar.nonterminals)
        self.assertNotIn("C", grammar.productions)

    def test_final_cnf_shape_validation(self) -> None:
        """All productions after to_cnf must match CNF production shapes."""
        grammar = build_sample_grammar()
        converter = CNFConverter(grammar)

        converter.to_cnf()

        for lhs, rhs_list in grammar.productions.items():
            self.assertIn(lhs, grammar.nonterminals)
            self.assertEqual(len(rhs_list), len(set(rhs_list)))  # no duplicates

            for rhs in rhs_list:
                if len(rhs) == 1:
                    self.assertIn(rhs[0], grammar.terminals)
                elif len(rhs) == 2:
                    self.assertIn(rhs[0], grammar.nonterminals)
                    self.assertIn(rhs[1], grammar.nonterminals)
                else:
                    self.fail(f"Non-CNF rule found: {lhs} -> {rhs}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
