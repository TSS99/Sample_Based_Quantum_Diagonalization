#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "README.md",
    ROOT / "scripts" / "generate_sqd_notebook.py",
    ROOT / "notebooks" / "sample_based_quantum_diagonalization_workflow.ipynb",
]
BAD_TOKENS = [r"\(", r"\)", r"\[", r"\]"]


def main() -> None:
    failed = False

    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for token in BAD_TOKENS:
            if token in text:
                failed = True
                print(f"{path}: found {token}")

    if failed:
        raise SystemExit(1)

    print("No GitHub-unfriendly math delimiters found.")


if __name__ == "__main__":
    main()
