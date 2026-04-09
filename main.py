"""Command-line runner for CFG to CNF conversion (Variant 18)."""

from __future__ import annotations

import sys
from pathlib import Path


# Allow running `python main.py` without installing the package.
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cfg_cnf import CNFConverter  # noqa: E402
from examples.sample_grammar import build_sample_grammar  # noqa: E402


def _print_stage(title: str, converter: CNFConverter) -> None:
    """Print one conversion stage in a terminal-friendly format."""
    print(f"\n=== {title} ===")
    print(converter.grammar.pretty().replace("\u03b5", "epsilon"))


def main() -> None:
    """
    Build Variant 18 grammar and run the full CNF pipeline step by step.
    """
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


if __name__ == "__main__":
    main()
