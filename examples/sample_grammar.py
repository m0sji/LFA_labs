"""Reusable grammar fixture for future CNF conversion tests."""

from __future__ import annotations

from cfg_cnf import Grammar

SAMPLE_NONTERMINALS = {"S", "A", "B", "C", "D"}
SAMPLE_TERMINALS = {"a", "b"}
SAMPLE_START_SYMBOL = "S"

SAMPLE_PRODUCTIONS = {
    "S": ["aB", "bA", "B"],
    "A": ["b", "aD", "AS", "bAB", "\u03b5"],
    "B": ["a", "bS"],
    "C": ["AB"],
    "D": ["BB"],
}


def build_sample_grammar() -> Grammar:
    """Build the sample grammar from Python data structures."""
    return Grammar.from_dict(
        nonterminals=SAMPLE_NONTERMINALS,
        terminals=SAMPLE_TERMINALS,
        productions=SAMPLE_PRODUCTIONS,
        start_symbol=SAMPLE_START_SYMBOL,
    )
