#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "sample_based_quantum_diagonalization_workflow.ipynb"


def markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": dedent(source).strip("\n").splitlines(keepends=True),
    }


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(source).strip("\n").splitlines(keepends=True),
    }


def build_notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.13",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def build_cells() -> list[dict]:
    return [
        markdown_cell(
            r"""
            # Sample-Based Quantum Diagonalization: A Beginner-Friendly Workflow

            This notebook is written as if we were sitting together at a whiteboard and building the idea slowly.

            The central question is:

            $$
            H \lvert \psi \rangle = E \lvert \psi \rangle
            $$

            where:

            - \(H\) is the Hamiltonian matrix,
            - \(E\) is an energy eigenvalue,
            - \(\lvert \psi \rangle\) is an eigenstate.

            In a large quantum problem, directly diagonalizing \(H\) can be too expensive. Sample-based quantum diagonalization (SQD) tries to avoid that by using samples to identify a much smaller subspace that still contains the important physics.

            In this notebook we will work through the full logic step by step, using a small toy Hamiltonian so every piece stays visible.
            """
        ),
        markdown_cell(
            r"""
            ## Step 1: Know the roadmap before touching the code

            Here is the plan we will follow:

            1. Define a small Hamiltonian \(H\).
            2. Solve it exactly so we know the correct answer.
            3. Convert the exact ground state into measurement probabilities.
            4. Draw samples from those probabilities to imitate repeated measurements.
            5. Use the most important sampled bitstrings to define a reduced subspace.
            6. Project \(H\) into that subspace.
            7. Solve the smaller projected eigenvalue problem.
            8. Compare the SQD estimate with the exact result.

            Mathematically, the reduced problem is

            $$
            H_{\mathrm{sub}} c = E S c,
            $$

            where \(H_{\mathrm{sub}}\) is the projected Hamiltonian and \(S\) is the overlap matrix. In our toy example the chosen basis states are orthonormal, so \(S\) will turn out to be the identity matrix, but it is useful to keep the general formula in view.
            """
        ),
        markdown_cell(
            r"""
            ## Step 2: Import the tools we need

            We keep the software stack intentionally small:

            - `numpy` for arrays and linear algebra bookkeeping,
            - `scipy.linalg.eigh` for Hermitian eigenvalue problems,
            - `pandas` for neat tables,
            - `matplotlib` for a few simple plots.

            The goal of this notebook is to make the algorithm transparent, not to hide it behind a large framework.
            """
        ),
        code_cell(
            """
            import numpy as np
            import pandas as pd
            import matplotlib.pyplot as plt
            from scipy.linalg import eigh

            np.set_printoptions(precision=4, suppress=True)
            plt.style.use("seaborn-v0_8-whitegrid")

            SEED = 7
            rng = np.random.default_rng(SEED)
            """
        ),
        markdown_cell(
            r"""
            ## Step 3: Define the Hamiltonian and the computational basis

            We use a three-qubit toy Hamiltonian, so the Hilbert space has dimension

            $$
            2^3 = 8.
            $$

            That means the computational basis is

            $$
            \{
            \lvert 000 \rangle,
            \lvert 001 \rangle,
            \lvert 010 \rangle,
            \lvert 011 \rangle,
            \lvert 100 \rangle,
            \lvert 101 \rangle,
            \lvert 110 \rangle,
            \lvert 111 \rangle
            \}.
            $$

            The matrix below is small enough to inspect directly, but rich enough to show the SQD idea clearly.
            """
        ),
        code_cell(
            """
            basis_labels = [format(i, "03b") for i in range(8)]

            H = np.array(
                [
                    [0.2235, -0.0390, -0.1035, -0.0818, 0.1746, 0.1091, 0.1165, -0.0104],
                    [-0.0390, 0.6621, 0.0706, -0.1964, -0.0782, 0.2619, 0.1095, 0.0029],
                    [-0.1035, 0.0706, 0.9961, 0.1724, 0.1067, -0.2299, -0.1817, 0.1571],
                    [-0.0818, -0.1964, 0.1724, -0.1773, 0.1019, -0.4778, -0.1272, -0.0414],
                    [0.1746, -0.0782, 0.1067, 0.1019, 0.1418, -0.1359, -0.1793, -0.0766],
                    [0.1091, 0.2619, -0.2299, -0.4778, -0.1359, 0.1014, 0.1696, 0.0552],
                    [0.1165, 0.1095, -0.1817, -0.1272, -0.1793, 0.1696, 0.4227, 0.2702],
                    [-0.0104, 0.0029, 0.1571, -0.0414, -0.0766, 0.0552, 0.2702, 0.4456],
                ]
            )

            hamiltonian_df = pd.DataFrame(H, index=basis_labels, columns=basis_labels)
            hamiltonian_df
            """
        ),
    ]


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    notebook = build_notebook(build_cells())
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
