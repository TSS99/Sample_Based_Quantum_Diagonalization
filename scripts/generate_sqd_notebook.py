#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "sample_based_quantum_diagonalization_workflow.ipynb"


def github_friendly_markdown(source: str) -> str:
    cleaned = dedent(source).strip("\n")
    return (
        cleaned.replace(r"\(", "$")
        .replace(r"\)", "$")
        .replace(r"\[", "$$")
        .replace(r"\]", "$$")
    )


def markdown_cell(source: str) -> dict:
    clean_source = github_friendly_markdown(source)
    return {
        "cell_type": "markdown",
        "id": "md-" + hashlib.sha1(clean_source.encode("utf-8")).hexdigest()[:10],
        "metadata": {},
        "source": clean_source.splitlines(keepends=True),
    }


def code_cell(source: str) -> dict:
    clean_source = dedent(source).strip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": "code-" + hashlib.sha1(clean_source.encode("utf-8")).hexdigest()[:10],
        "metadata": {},
        "outputs": [],
        "source": clean_source.splitlines(keepends=True),
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
        markdown_cell(
            r"""
            ## Step 4: Solve the full problem exactly

            Before we approximate anything, we should know the exact answer.

            Since \(H\) is a real symmetric matrix, we can use a Hermitian eigensolver to compute all eigenvalues and eigenvectors. The smallest eigenvalue is the ground-state energy.

            In symbols, we are looking for

            $$
            E_0 = \min \mathrm{spec}(H),
            $$

            and for the corresponding normalized eigenvector \(\lvert \psi_0 \rangle\).

            This exact solution will be our benchmark for judging whether the sample-based approach worked.
            """
        ),
        code_cell(
            """
            exact_eigenvalues, exact_eigenvectors = eigh(H)
            exact_ground_energy = exact_eigenvalues[0]
            exact_ground_state = exact_eigenvectors[:, 0]

            energy_table = pd.DataFrame(
                {
                    "eigenvalue": exact_eigenvalues,
                }
            )

            print(f"Exact ground-state energy: {exact_ground_energy:.6f}")
            energy_table
            """
        ),
        markdown_cell(
            r"""
            ## Step 5: Inspect the exact ground state in the computational basis

            Any state in this eight-dimensional Hilbert space can be expanded as

            $$
            \lvert \psi_0 \rangle = \sum_x a_x \lvert x \rangle,
            $$

            where each \(x\) is a bitstring such as \(011\) or \(101\), and \(a_x\) is the corresponding amplitude.

            The measurement probability of each basis state is given by the Born rule:

            $$
            p(x) = |a_x|^2.
            $$

            If SQD is going to work, our samples need to repeatedly reveal the basis states that carry most of this probability weight.
            """
        ),
        code_cell(
            """
            support_df = pd.DataFrame(
                {
                    "bitstring": basis_labels,
                    "amplitude": exact_ground_state,
                    "probability": np.abs(exact_ground_state) ** 2,
                }
            ).sort_values("probability", ascending=False, ignore_index=True)

            support_df
            """
        ),
        markdown_cell(
            r"""
            ## Step 6: Emulate repeated measurements

            In a real quantum workflow, we would prepare a state on hardware or on a simulator and then measure it many times. Each shot returns one computational basis state.

            To keep this notebook focused on the SQD logic, we will emulate that measurement process directly from the exact probabilities.

            If the true distribution is \(p(x)\), then a finite number of shots will not reproduce it perfectly. That finite-shot noise is important because it affects which basis states we keep in our reduced subspace.
            """
        ),
        code_cell(
            """
            shots = 300
            sampled_indices = rng.choice(len(basis_labels), size=shots, p=np.abs(exact_ground_state) ** 2)
            counts = pd.Series(sampled_indices).value_counts().sort_values(ascending=False)

            counts_df = pd.DataFrame(
                {
                    "decimal": counts.index,
                    "bitstring": [basis_labels[i] for i in counts.index],
                    "count": counts.values,
                }
            )
            counts_df["empirical_probability"] = counts_df["count"] / shots

            counts_df
            """
        ),
        markdown_cell(
            r"""
            ## Step 7: Turn the samples into a candidate subspace

            The SQD idea is simple:

            - frequent bitstrings are likely to matter,
            - rare or unseen bitstrings may matter less,
            - so we build a reduced subspace from the configurations that appear most often.

            In this toy problem the exact ground state mostly lives on two basis states, so we will keep the two most frequently observed bitstrings.

            If the sampling step is informative, these two bitstrings should match the important support of the exact ground state.
            """
        ),
        code_cell(
            """
            top_k = 2
            selected_indices = counts_df.head(top_k)["decimal"].tolist()
            selected_bitstrings = [basis_labels[i] for i in selected_indices]

            B = np.eye(len(basis_labels))[:, selected_indices]

            print("Selected basis states:", selected_bitstrings)
            print("Shape of basis matrix B:", B.shape)
            """
        ),
        markdown_cell(
            r"""
            ## Step 8: Project the Hamiltonian into the sampled subspace

            Once we have the basis matrix \(B\), the projected Hamiltonian is

            $$
            H_{\mathrm{sub}} = B^T H B.
            $$

            The overlap matrix is

            $$
            S = B^T B.
            $$

            Because the columns of \(B\) are computational basis vectors, they are orthonormal, so \(S = I\). Still, we compute it explicitly because the more general SQD workflow often involves a nontrivial overlap matrix.
            """
        ),
        code_cell(
            """
            H_sub = B.T @ H @ B
            S_sub = B.T @ B

            print("Projected Hamiltonian:")
            print(H_sub)
            print()
            print("Overlap matrix:")
            print(S_sub)
            """
        ),
        markdown_cell(
            r"""
            ## Step 9: Solve the reduced eigenvalue problem

            The reduced coefficients \(c\) satisfy

            $$
            H_{\mathrm{sub}} c = E S c.
            $$

            The smallest eigenvalue of this reduced problem is our SQD energy estimate. Once we have the coefficient vector \(c\), we lift it back into the original Hilbert space with

            $$
            \lvert \psi_{\mathrm{SQD}} \rangle = B c.
            $$

            This step is the payoff: a small diagonalization problem replaces the full one.
            """
        ),
        code_cell(
            """
            sqd_eigenvalues, sqd_eigenvectors = eigh(H_sub, S_sub)
            sqd_energy = sqd_eigenvalues[0]
            sqd_coefficients = sqd_eigenvectors[:, 0]
            sqd_state = B @ sqd_coefficients

            print(f"SQD ground-state estimate: {sqd_energy:.6f}")
            print("Reduced-space coefficients:")
            print(sqd_coefficients)
            print("Reconstructed state in the full basis:")
            print(sqd_state)
            """
        ),
        markdown_cell(
            r"""
            ## Step 10: Compare the SQD estimate with the exact answer

            There are two natural diagnostics:

            1. **Energy error**
               $$
               |E_{\mathrm{SQD}} - E_0|
               $$
            2. **State overlap**
               $$
               |\langle \psi_0 \vert \psi_{\mathrm{SQD}} \rangle|
               $$

            An overlap close to \(1\) means the approximate state points in almost the same direction as the exact ground state.
            """
        ),
        code_cell(
            """
            energy_error = abs(sqd_energy - exact_ground_energy)
            state_overlap = abs(np.vdot(exact_ground_state, sqd_state))

            comparison_df = pd.DataFrame(
                {
                    "metric": ["Exact ground energy", "SQD ground energy", "Absolute energy error", "State overlap"],
                    "value": [exact_ground_energy, sqd_energy, energy_error, state_overlap],
                }
            )

            comparison_df
            """
        ),
        markdown_cell(
            r"""
            ## Step 11: Study how shot count and subspace size affect the answer

            SQD is only as good as the subspace suggested by the samples.

            Two knobs matter a lot:

            - the number of measurement shots,
            - the number of sampled configurations we keep.

            The experiment below repeats the workflow many times and records the average energy error. This is useful because a single random draw can be lucky or unlucky.
            """
        ),
        code_cell(
            """
            def run_sqd_trial(shots: int, top_k: int, seed: int) -> float:
                local_rng = np.random.default_rng(seed)
                sampled = local_rng.choice(len(basis_labels), size=shots, p=np.abs(exact_ground_state) ** 2)
                counts = pd.Series(sampled).value_counts().sort_values(ascending=False)
                chosen = counts.head(top_k).index.tolist()
                B_trial = np.eye(len(basis_labels))[:, chosen]
                H_trial = B_trial.T @ H @ B_trial
                S_trial = B_trial.T @ B_trial
                trial_energy = eigh(H_trial, S_trial)[0][0]
                return abs(trial_energy - exact_ground_energy)


            shot_grid = [8, 16, 32, 64, 128, 256, 512]
            subspace_grid = [1, 2, 3]
            rows = []

            for shots_value in shot_grid:
                for subspace_size in subspace_grid:
                    errors = [
                        run_sqd_trial(shots=shots_value, top_k=subspace_size, seed=1000 + rep)
                        for rep in range(40)
                    ]
                    rows.append(
                        {
                            "shots": shots_value,
                            "subspace_size": subspace_size,
                            "mean_abs_energy_error": float(np.mean(errors)),
                        }
                    )

            experiment_df = pd.DataFrame(rows)
            experiment_df
            """
        ),
        markdown_cell(
            r"""
            ## Step 12: Visualize the convergence trend

            We expect the energy error to improve when:

            - we collect more shots, because the empirical distribution better matches the true one,
            - we allow a slightly larger subspace, because we reduce the chance of excluding an important basis state.

            The plot below helps us see that trend instead of guessing it from a table.
            """
        ),
        code_cell(
            """
            fig, ax = plt.subplots(figsize=(8, 5))

            for subspace_size, group in experiment_df.groupby("subspace_size"):
                ax.plot(
                    group["shots"],
                    group["mean_abs_energy_error"],
                    marker="o",
                    linewidth=2,
                    label=f"top_k = {subspace_size}",
                )

            ax.set_xscale("log", base=2)
            ax.set_xlabel("Number of shots")
            ax.set_ylabel("Mean absolute energy error")
            ax.set_title("How finite-shot sampling affects SQD accuracy")
            ax.legend()
            plt.show()
            """
        ),
        markdown_cell(
            r"""
            ## Step 13: Show a failure case on purpose

            Good examples teach success.
            Great examples also teach failure.

            If our subspace misses an important ground-state basis vector, the projected problem cannot recover the correct energy. We will now choose a deliberately bad subspace to see this happen in practice.
            """
        ),
        code_cell(
            """
            bad_indices = [0, 3, 6]  # |000>, |011>, |110>
            B_bad = np.eye(len(basis_labels))[:, bad_indices]
            H_bad = B_bad.T @ H @ B_bad
            S_bad = B_bad.T @ B_bad
            bad_energy = eigh(H_bad, S_bad)[0][0]

            print("Bad subspace bitstrings:", [basis_labels[i] for i in bad_indices])
            print(f"Energy from the bad subspace: {bad_energy:.6f}")
            print(f"Exact ground-state energy:   {exact_ground_energy:.6f}")
            """
        ),
        markdown_cell(
            r"""
            ## Step 14: What this notebook should leave you with

            The full SQD workflow is now visible:

            1. Solve or estimate a state whose measurements reveal important basis states.
            2. Sample bitstrings from that state.
            3. Keep the configurations that appear important.
            4. Build a reduced basis matrix \(B\).
            5. Form \(H_{\mathrm{sub}} = B^T H B\) and \(S = B^T B\).
            6. Solve the reduced eigenvalue problem.
            7. Check whether the answer converges as you increase shots or enrich the subspace.

            In larger chemistry or materials problems, the same logic is used, but the state preparation, symmetry constraints, and Hamiltonian construction become more sophisticated.

            The core lesson stays the same:

            $$
            \text{good samples} \longrightarrow \text{good subspace} \longrightarrow \text{good reduced diagonalization}.
            $$
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
