#!/usr/bin/env python3
"""Validate SPL syntax before execution."""

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from error_handler import handle_errors
from formatters import format_json, print_success, print_warning
from spl_helper import (
    estimate_search_complexity,
    optimize_spl,
    parse_spl_commands,
    validate_spl_syntax,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Validate SPL syntax")
    parser.add_argument("spl", help="SPL query to validate")
    parser.add_argument(
        "--suggestions", "-s", action="store_true", help="Show optimization suggestions"
    )
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    is_valid, issues = validate_spl_syntax(args.spl)
    commands = parse_spl_commands(args.spl)
    complexity = estimate_search_complexity(args.spl)
    _, suggestions = optimize_spl(args.spl)

    if args.output == "json":
        print(
            format_json(
                {
                    "valid": is_valid,
                    "issues": issues,
                    "commands": [{"name": c[0], "args": c[1]} for c in commands],
                    "complexity": complexity,
                    "suggestions": suggestions if args.suggestions else [],
                }
            )
        )
    else:
        if is_valid:
            print_success("SPL syntax is valid")
        else:
            print_warning("SPL syntax issues found:")
            for issue in issues:
                print(f"  - {issue}")

        print(f"\nComplexity: {complexity}")
        print(f"Commands: {' | '.join(c[0] for c in commands)}")

        if args.suggestions and suggestions:
            print("\nOptimization suggestions:")
            for s in suggestions:
                print(f"  - {s}")


if __name__ == "__main__":
    main()
