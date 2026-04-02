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

            - $H$ is the Hamiltonian matrix,
            - $E$ is an energy eigenvalue,
            - $\lvert \psi \rangle$ is an eigenstate.

            In a large quantum problem, directly diagonalizing $H$ can be too expensive. Sample-based quantum diagonalization (SQD) tries to avoid that by using samples to identify a much smaller subspace that still contains the important physics.

            In this notebook we will work through the full logic step by step, using a small toy Hamiltonian so every piece stays visible.

            By the end of the notebook, you should be able to answer all of these questions clearly:

            - What problem are we solving when we diagonalize a Hamiltonian?
            - Why do basis states and measurement samples matter?
            - How do we go from raw bitstrings to a reduced matrix problem?
            - Why can a smaller projected eigenvalue problem still give a good approximation?

            You do **not** need to be an expert in quantum computing before starting. The notebook explains the ideas from first principles and keeps reminding you what each symbol and each code cell is doing.
            """
        ),
        markdown_cell(
            r"""
            ## How to use this notebook well

            This notebook is designed to be studied slowly rather than skimmed quickly.

            A good rhythm is:

            1. Read one markdown cell carefully.
            2. Predict what the next code cell is going to show.
            3. Run the code cell.
            4. Compare the output to your expectation.
            5. Ask yourself what new mathematical object was created in that step.

            If you do that consistently, the notebook becomes much easier to follow because every code cell has a clear job in the larger workflow.
            """
        ),
        markdown_cell(
            r"""
            ## Step 1: Know the roadmap before touching the code

            Here is the plan we will follow:

            1. Define a small Hamiltonian $H$.
            2. Solve it exactly so we know the correct answer.
            3. Convert the exact ground state into measurement probabilities.
            4. Draw samples from those probabilities to imitate repeated measurements.
            5. Use the most important sampled bitstrings to define a reduced subspace.
            6. Project $H$ into that subspace.
            7. Solve the smaller projected eigenvalue problem.
            8. Compare the SQD estimate with the exact result.

            Mathematically, the reduced problem is

            $$
            H_{\mathrm{sub}} c = E S c,
            $$

            where $H_{\mathrm{sub}}$ is the projected Hamiltonian and $S$ is the overlap matrix. In our toy example the chosen basis states are orthonormal, so $S$ will turn out to be the identity matrix, but it is useful to keep the general formula in view.

            You can summarize the notebook in one equation chain:

            $$
            H \;\Longrightarrow\; \lvert \psi_0 \rangle \;\Longrightarrow\; p(x) \;\Longrightarrow\; \hat{p}(x) \;\Longrightarrow\; B \;\Longrightarrow\; H_{\mathrm{sub}} c = E S c.
            $$

            Each arrow means "use the previous object to build the next one."
            """
        ),
        markdown_cell(
            r"""
            ## What you need to know before continuing

            This notebook assumes only a very small amount of background:

            - you know that matrices act on vectors,
            - you know that eigenvalues and eigenvectors come from linear algebra,
            - you are willing to think of a quantum state as a vector with a probability interpretation.

            If any of that still feels shaky, that is okay. The notebook keeps translating between quantum language and ordinary linear algebra language so you never have to rely on jargon alone.
            """
        ),
        markdown_cell(
            r"""
            ## Mathematical assumptions used in this notebook

            We will be very explicit about what assumptions are being made, because that makes the later calculations much easier to trust.

            In this notebook we assume:

            1. The Hilbert space is finite-dimensional, so every state can be written as a finite column vector.
            2. We work in the computational basis, which means basis states are orthonormal.
            3. The Hamiltonian is represented by a real symmetric matrix, so Hermitian linear algebra applies and all eigenvalues are real.
            4. The ground-state vector is normalized, so its squared amplitudes form a valid probability distribution.
            5. Sampling is performed from that probability distribution with a finite number of shots.

            None of those assumptions are exotic, but writing them down clearly helps us understand why each mathematical step later is legitimate.
            """
        ),
        markdown_cell(
            r"""
            ## Section map

            To make the notebook easier to navigate, here is the role of each major block:

            - **Steps 1-3** set up the notation, basis, and Hamiltonian.
            - **Steps 4-5** solve the exact problem and inspect the true ground state.
            - **Steps 6-7** imitate measurements and choose a reduced basis from samples.
            - **Steps 8-10** solve the reduced problem and compare it with the exact answer.
            - **Steps 11-14** test robustness, show failure, and summarize the full idea.

            If you ever feel lost, come back to this map and ask which of those five jobs the current cell belongs to.
            """
        ),
        markdown_cell(
            r"""
            ## A quick notation primer before we compute anything

            If Dirac notation is new to you, here is the minimum you need for this notebook:

            - $\lvert x \rangle$ means a basis state. In this notebook, $x$ is usually a three-bit string like $011$.
            - A state such as $\lvert \psi \rangle$ is a vector made from a weighted combination of basis states.
            - The weights in that combination are called amplitudes.
            - Squaring the magnitude of an amplitude gives a measurement probability.

            In ordinary linear algebra language, you can think of this notebook as solving a matrix eigenvalue problem and then approximating it inside a carefully chosen smaller vector space.

            That means you can read the notebook in two equivalent ways:

            - as a quantum story about states and measurements,
            - or as a numerical linear algebra story about vectors, probabilities, and projections.

            There are also a few dimensions worth keeping in mind:

            - the full state vector has length $8$ because $2^3 = 8$,
            - the Hamiltonian is therefore an $8 \times 8$ matrix,
            - later, the reduced-basis coefficient vector $c$ will be shorter than length $8$ because it lives in the sampled subspace.

            So whenever you see a new symbol, you should ask two simple questions:

            1. Is this object a scalar, a vector, or a matrix?
            2. Which space does it live in: the full $8$-dimensional space, or the smaller reduced subspace?

            We will also use the computational basis as an orthonormal basis, which means

            $$
            \langle x \vert y \rangle =
            \begin{cases}
            1, & x = y, \\
            0, & x \neq y.
            \end{cases}
            $$

            This orthonormality assumption is what lets us move cleanly between basis expansions, amplitudes, and probabilities.
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

            In other words, every library here has a simple job:

            - `numpy` stores the vectors and matrices,
            - `scipy` solves the eigenvalue problems,
            - `pandas` lets us inspect results in a readable table,
            - `matplotlib` helps us see convergence instead of only reading numbers.

            The code cell also fixes a random seed. That matters because the sampling stage is stochastic. Using a seed means you and I can reproduce the same example and talk about the same outputs.
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

            More generally, for $n$ qubits,

            $$
            \dim(\mathcal{H}) = 2^n.
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

            In coordinate form, a general state in this basis looks like

            $$
            \lvert \psi \rangle =
            a_{000}\lvert 000 \rangle +
            a_{001}\lvert 001 \rangle +
            \cdots +
            a_{111}\lvert 111 \rangle.
            $$

            If we stack the amplitudes into a column vector, then the same state is also represented by

            $$
            \lvert \psi \rangle
            \leftrightarrow
            \begin{bmatrix}
            a_{000} \\
            a_{001} \\
            \vdots \\
            a_{111}
            \end{bmatrix}.
            $$

            A useful beginner mindset is this:

            - each **row** and **column** corresponds to one basis state,
            - each matrix entry tells us how those basis states are energetically related,
            - diagonal entries describe energies tied to individual basis states,
            - off-diagonal entries describe couplings or mixing between different basis states.

            More formally, the matrix entries are

            $$
            H_{xy} = \langle x \vert H \vert y \rangle,
            $$

            so each number tells us how the Hamiltonian connects basis state $\lvert y \rangle$ to basis state $\lvert x \rangle$.

            In a larger problem you would almost never print the whole Hamiltonian, but here it is worth doing once because it makes the abstract notation concrete.

            There are also two important mathematical facts hiding in plain sight:

            1. Because the matrix is symmetric, it has a complete set of orthonormal eigenvectors.
            2. Because it is real symmetric, all of its eigenvalues are real numbers.

            Those facts are exactly why diagonalization is such a natural thing to do here.
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
        code_cell(
            """
            basis_lookup_df = pd.DataFrame(
                {
                    "decimal_index": list(range(len(basis_labels))),
                    "bitstring": basis_labels,
                }
            )

            basis_lookup_df
            """
        ),
        code_cell(
            """
            example_state = pd.Series(np.eye(len(basis_labels))[:, 3], index=basis_labels, name="|011>")
            example_state
            """
        ),
        markdown_cell(
            r"""
            ### What to notice in the Hamiltonian table

            When you look at the matrix above, you do **not** need to memorize every number.

            Instead, notice these structural facts:

            1. The matrix is symmetric, which is why a Hermitian eigensolver is appropriate.
            2. The problem lives in an eight-dimensional space because we chose three qubits.
            3. Off-diagonal couplings mean the true eigenstates will usually be superpositions rather than single basis states.

            That last point is especially important. If the ground state were just one basis vector, there would be much less for SQD to discover from sampling.
            """
        ),
        markdown_cell(
            r"""
            ### Why the one-hot basis example helps

            The short vector printed above shows what a single computational basis state looks like in coordinates.

            For example, $\lvert 011 \rangle$ appears as a vector with:

            - a single $1$ in the row labeled $011$,
            - and $0$ everywhere else.

            Later in the notebook, superposition states are built by combining these basis vectors with different amplitudes. Seeing one basis vector explicitly first makes that idea easier to picture.
            """
        ),
        markdown_cell(
            r"""
            ### Why the basis lookup table matters

            The notebook will sometimes move back and forth between:

            - a **decimal index** such as $3$,
            - and a **bitstring label** such as $011$.

            They refer to the same basis state, just written in two different ways.

            Keeping that translation visible helps a lot later when we sample integer indices from arrays but want to interpret the results as measured bitstrings.
            """
        ),
        markdown_cell(
            r"""
            ## Step 4: Solve the full problem exactly

            Before we approximate anything, we should know the exact answer.

            Since $H$ is a real symmetric matrix, we can use a Hermitian eigensolver to compute all eigenvalues and eigenvectors. The smallest eigenvalue is the ground-state energy.

            In symbols, we are looking for

            $$
            E_0 = \min \mathrm{spec}(H),
            $$

            and for the corresponding normalized eigenvector $\lvert \psi_0 \rangle$.

            This exact solution will be our benchmark for judging whether the sample-based approach worked.

            Said more plainly:

            - the **eigenvalues** are the allowed energies of the system,
            - the **lowest** eigenvalue is the ground-state energy,
            - the matching eigenvector tells us how the ground state is spread across the basis states.

            We do this exact solve first because SQD is an approximation method. Without a trusted reference, it would be much harder to tell whether the reduced subspace is actually good.

            Another way to say this is that diagonalization writes the Hamiltonian in a basis where it acts as simply as possible. In that eigenbasis, each eigenvector is only scaled by its eigenvalue rather than mixed with the others.

            Written step by step, the eigenvalue equation says:

            $$
            H \lvert \psi_i \rangle = E_i \lvert \psi_i \rangle.
            $$

            That means:

            1. start with the vector $\lvert \psi_i \rangle$,
            2. apply the matrix $H$,
            3. the output points in the **same direction** as $\lvert \psi_i \rangle$,
            4. the only change is a scaling by the number $E_i$.

            So an eigenvector is a direction that the matrix does not rotate away from itself, and the eigenvalue tells you the scaling attached to that direction.

            For a symmetric matrix, the full eigendecomposition can be written as

            $$
            H = \sum_i E_i \lvert \psi_i \rangle \langle \psi_i \rvert,
            $$

            which means the entire Hamiltonian can be reconstructed from its eigenvalues and orthonormal eigenvectors.

            For a normalized trial state $\lvert \phi \rangle$, the energy expectation is

            $$
            \frac{\langle \phi \rvert H \lvert \phi \rangle}{\langle \phi \vert \phi \rangle}.
            $$

            The ground-state energy is the minimum value of this expression over all nonzero trial states, which is why subspace methods focus so much on choosing good trial spaces.
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
        code_cell(
            """
            normalization_check = np.linalg.norm(exact_ground_state)
            print(f"Norm of the exact ground-state vector: {normalization_check:.6f}")
            """
        ),
        markdown_cell(
            r"""
            ### How to read the exact output

            The printed number is the best ground-state energy available for this toy Hamiltonian because it comes from the full matrix.

            The table contains **all** eigenvalues, not just the smallest one. That matters because it reminds us that diagonalization gives the full energy spectrum.

            For SQD, however, we mostly care about the lowest eigenvalue and its eigenvector, because that is the state whose measurement samples we will study next.
            """
        ),
        markdown_cell(
            r"""
            ### Why checking normalization is a good habit

            A valid quantum state should have norm $1$.

            In symbols,

            $$
            \sum_x |a_x|^2 = 1.
            $$

            This follows directly from orthonormality:

            $$
            \langle \psi \vert \psi \rangle
            =
            \sum_{x,y} a_x^* a_y \langle x \vert y \rangle
            =
            \sum_x |a_x|^2.
            $$

            Printing the norm is a simple sanity check. It reassures us that the eigenvector we are about to interpret probabilistically really can be used to define a proper probability distribution.
            """
        ),
        markdown_cell(
            r"""
            ## Step 5: Inspect the exact ground state in the computational basis

            Any state in this eight-dimensional Hilbert space can be expanded as

            $$
            \lvert \psi_0 \rangle = \sum_x a_x \lvert x \rangle,
            $$

            where each $x$ is a bitstring such as $011$ or $101$, and $a_x$ is the corresponding amplitude.

            The measurement probability of each basis state is given by the Born rule:

            $$
            p(x) = |a_x|^2.
            $$

            This formula is doing two jobs at once:

            1. It turns the linear algebra object $\lvert \psi_0 \rangle$ into a probability model.
            2. It explains why even a state with positive and negative amplitudes can still lead to nonnegative probabilities.

            In our finite basis, the logic is:

            $$
            \lvert \psi_0 \rangle = \sum_x a_x \lvert x \rangle
            \quad \Longrightarrow \quad
            p(x) = |a_x|^2.
            $$

            Then normalization tells us

            $$
            \sum_x p(x) = \sum_x |a_x|^2 = 1.
            $$

            So the amplitudes are not probabilities themselves, but their squared magnitudes produce a valid probability distribution.

            For example, if the coefficient in front of $\lvert 011 \rangle$ is $a_{011}$, then the probability of measuring the bitstring $011$ is

            $$
            p(011) = |a_{011}|^2.
            $$

            If SQD is going to work, our samples need to repeatedly reveal the basis states that carry most of this probability weight.

            This is one of the central ideas of the whole notebook:

            - the eigenvector contains amplitude information,
            - the amplitudes determine probabilities,
            - the probabilities tell us which basis states show up often when we measure,
            - the frequently observed states become candidates for our reduced subspace.
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
        code_cell(
            """
            support_df["cumulative_probability"] = support_df["probability"].cumsum()
            support_df
            """
        ),
        code_cell(
            """
            total_exact_probability = support_df["probability"].sum()
            print(f"Total exact probability: {total_exact_probability:.6f}")
            """
        ),
        markdown_cell(
            r"""
            ### How to interpret the support table

            Read the table from top to bottom.

            The largest probabilities tell you where the ground state "lives" most strongly in the computational basis. Those high-probability bitstrings are exactly the ones we hope to recover from sampling.

            If the probability mass were spread almost uniformly over all eight basis states, SQD would have much less of an advantage here. The method becomes attractive when important information is concentrated in a smaller part of the full space.
            """
        ),
        markdown_cell(
            r"""
            ### Why summing the probabilities is a useful beginner check

            The total exact probability should be $1$.

            That statement may sound obvious, but it is a helpful checkpoint because it reminds us that the ground-state vector is being interpreted as a genuine probability distribution over basis states.

            Whenever you work with amplitudes and probabilities, little sanity checks like this help keep the story mathematically grounded.
            """
        ),
        markdown_cell(
            r"""
            ### Why cumulative probability is helpful

            The cumulative column answers a beginner-friendly question:

            **How much of the whole state have I already captured if I keep only the top few basis states?**

            If the probabilities are sorted in descending order,

            $$
            p_1 \ge p_2 \ge \cdots \ge p_8,
            $$

            then the cumulative probability after keeping the first $m$ rows is

            $$
            C_m = \sum_{j=1}^m p_j.
            $$

            If the cumulative probability rises quickly, that means a small subset of basis states carries a large fraction of the total weight. Situations like that are exactly where sample-based subspace methods become attractive.
            """
        ),
        markdown_cell(
            r"""
            ## Step 6: Emulate repeated measurements

            In a real quantum workflow, we would prepare a state on hardware or on a simulator and then measure it many times. Each shot returns one computational basis state.

            To keep this notebook focused on the SQD logic, we will emulate that measurement process directly from the exact probabilities.

            If the true distribution is $p(x)$, then a finite number of shots will not reproduce it perfectly. That finite-shot noise is important because it affects which basis states we keep in our reduced subspace.

            Here is the practical meaning of the code cell below:

            1. We choose a number of shots.
            2. We sample that many bitstrings from the exact probability distribution.
            3. We count how often each bitstring appears.
            4. We turn those counts into empirical probabilities.

            This is the bridge between the exact state vector and the sample-based workflow.

            Mathematically, we are replacing exact probabilities with estimates based on finitely many random draws. So from this point onward, the workflow contains both:

            - a deterministic object: the true probability distribution,
            - a random object: the finite sample drawn from that distribution.

            If the number of shots is $N$, then the expected number of times a bitstring $x$ appears is

            $$
            \mathbb{E}[\text{count}(x)] = N p(x).
            $$

            Dividing by $N$ gives the empirical probability estimate

            $$
            \hat{p}(x) = \frac{\text{count}(x)}{N}.
            $$
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
        code_cell(
            """
            probability_comparison_df = (
                support_df[["bitstring", "probability"]]
                .merge(counts_df[["bitstring", "empirical_probability"]], on="bitstring", how="left")
                .fillna({"empirical_probability": 0.0})
                .sort_values("probability", ascending=False, ignore_index=True)
            )

            probability_comparison_df
            """
        ),
        code_cell(
            """
            total_empirical_probability = counts_df["empirical_probability"].sum()
            print(f"Total empirical probability: {total_empirical_probability:.6f}")
            """
        ),
        markdown_cell(
            r"""
            ### What the measurement table is telling us

            The measurement table is a noisy estimate of the true probability distribution.

            A beginner-friendly way to think about it is:

            - the support table from the previous step shows the **true** probabilities,
            - this counts table shows a **finite-sample approximation** to those probabilities.

            The more shots we take, the closer the empirical table should move toward the true one on average. That is why shot count matters later when we study convergence.
            """
        ),
        markdown_cell(
            r"""
            ### Why the empirical probabilities should also sum to one

            We built the empirical probabilities by dividing each count by the total number of shots.

            That means the empirical probabilities should add up to $1$ as well. Checking that is a quick way to reassure yourself that the counts table is being interpreted correctly before you use it to choose a reduced basis.
            """
        ),
        markdown_cell(
            r"""
            ### How to read the true-vs-empirical comparison table

            This new table puts the exact probabilities and the sampled probabilities side by side.

            That makes it easier to see two things at once:

            - where the sampling is already doing a good job,
            - and where finite-shot noise is still distorting the picture.

            If the most important rows line up reasonably well, then our sampling stage is already giving us a useful clue about which basis states deserve a place in the reduced subspace.

            A natural row-by-row difference to keep in mind is

            $$
            \hat{p}(x) - p(x),
            $$

            which measures how far the sampled estimate is from the exact probability for that basis state.
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

            In matrix language, we are now choosing the columns that will define our reduced basis. In physics language, we are deciding which measured configurations are important enough to keep.

            The key approximation assumption here is:

            **the basis states that matter most for the target eigenstate are likely to appear most often in the samples.**

            SQD works well when that assumption is reasonably true and works poorly when important basis states are missed or badly under-sampled.

            In symbols, if we keep $k$ sampled bitstrings, we are approximately selecting the indices with the largest empirical probabilities:

            $$
            \{x_1, \dots, x_k\}
            \approx
            \operatorname*{arg\,topk}_x \hat{p}(x).
            $$

            Everything that follows depends on this reduced set being a good summary of the important support of the exact state.
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
        code_cell(
            """
            B_df = pd.DataFrame(B, index=basis_labels, columns=[f"chosen_{bitstring}" for bitstring in selected_bitstrings])
            B_df
            """
        ),
        code_cell(
            """
            exact_top_bitstrings = support_df.head(top_k)["bitstring"].tolist()
            selection_check_df = pd.DataFrame(
                {
                    "role": ["top exact support", "sample-chosen subspace"],
                    "bitstrings": [", ".join(exact_top_bitstrings), ", ".join(selected_bitstrings)],
                }
            )

            selection_check_df
            """
        ),
        markdown_cell(
            r"""
            ### What the basis matrix $B$ is really doing

            The matrix $B$ is a very concrete object:

            - it has one column for each basis state we kept,
            - each column is a standard basis vector in the full Hilbert space,
            - multiplying by $B$ maps reduced coordinates back into the full eight-dimensional space.

            For many beginners, this is the first moment when the reduced-basis idea really clicks, because $B$ is the object that physically connects the small problem to the original big one.
            """
        ),
        markdown_cell(
            r"""
            ### Why compare the sampled choice to the exact top support

            This comparison is a gentle diagnostic.

            It asks:

            **Did the finite-shot sampling recover the same important basis states that the exact state told us to expect?**

            When the answer is mostly yes, the reduced subspace is starting from a strong position. When the answer is no, the later reduced diagonalization has a much harder job.
            """
        ),
        markdown_cell(
            r"""
            ## Step 8: Project the Hamiltonian into the sampled subspace

            Once we have the basis matrix $B$, the projected Hamiltonian is

            $$
            H_{\mathrm{sub}} = B^T H B.
            $$

            The overlap matrix is

            $$
            S = B^T B.
            $$

            Because the columns of $B$ are computational basis vectors, they are orthonormal, so $S = I$. Still, we compute it explicitly because the more general SQD workflow often involves a nontrivial overlap matrix.

            This projection step is the mathematical heart of the approximation:

            - the full Hamiltonian acts on the full eight-dimensional space,
            - the basis matrix $B$ selects only the sampled directions we decided to keep,
            - $B^T H B$ asks how the original Hamiltonian behaves **inside that smaller space**.

            So after this step, we are no longer solving the original full problem directly. We are solving its restriction to a reduced subspace suggested by the samples.

            If you like dimensions, the matrix sizes are:

            - $H$ is $8 \times 8$,
            - $B$ is $8 \times k$,
            - $B^T$ is $k \times 8$,
            - so $B^T H B$ is $k \times k$.

            That is the whole computational payoff in one line: the big matrix is turned into a smaller matrix.

            If you want to see the algebra step by step, let $\lvert \phi \rangle$ be a trial state built from the reduced basis:

            $$
            \lvert \phi \rangle = B c.
            $$

            Then its energy expectation value is

            $$
            \langle \phi \rvert H \lvert \phi \rangle
            = (B c)^T H (B c)
            = c^T (B^T H B) c.
            $$

            The corresponding norm is

            $$
            \langle \phi \vert \phi \rangle
            = (B c)^T (B c)
            = c^T (B^T B) c.
            $$

            This is the precise reason the projected Hamiltonian is $H_{\mathrm{sub}} = B^T H B$ and the overlap matrix is $S = B^T B$.
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
        code_cell(
            """
            dimension_summary_df = pd.DataFrame(
                {
                    "space": ["full Hilbert space", "reduced sampled subspace"],
                    "dimension": [H.shape[0], H_sub.shape[0]],
                }
            )

            dimension_summary_df
            """
        ),
        markdown_cell(
            r"""
            ### Why the overlap matrix is worth computing even when it is simple

            In this toy example, $S$ becomes the identity because we selected ordinary computational basis vectors.

            That might make the overlap matrix feel unnecessary, but it is still a good habit to include it because many practical reduced-basis methods use vectors that are **not** automatically orthonormal.

            Thinking in terms of both $H_{\mathrm{sub}}$ and $S$ prepares you for the more general version of SQD used in real research workflows.
            """
        ),
        markdown_cell(
            r"""
            ### Why the dimension table is worth looking at

            SQD is motivated by scale, so it helps to make the size reduction explicit.

            Even in this small toy example, the table reminds us that we intentionally moved from the full problem to a smaller one. In realistic settings, that reduction can be much more dramatic, which is why the method is interesting in the first place.
            """
        ),
        markdown_cell(
            r"""
            ## Step 9: Solve the reduced eigenvalue problem

            The reduced coefficients $c$ satisfy

            $$
            H_{\mathrm{sub}} c = E S c.
            $$

            The smallest eigenvalue of this reduced problem is our SQD energy estimate. Once we have the coefficient vector $c$, we lift it back into the original Hilbert space with

            $$
            \lvert \psi_{\mathrm{SQD}} \rangle = B c.
            $$

            This step is the payoff: a small diagonalization problem replaces the full one.

            There are really two layers here:

            1. We solve for the best coefficients **inside the reduced basis**.
            2. We map those coefficients back to the original full space.

            That second step matters because it lets us compare the SQD approximation to the exact eigenvector using the same full-space coordinates.

            The reduced eigenvalue equation also has a clean derivation. Start with the trial state

            $$
            \lvert \phi \rangle = B c.
            $$

            If the basis is not assumed orthonormal, then the norm of this state is

            $$
            \langle \phi \rvert \phi \rangle
            = (B c)^T (B c)
            = c^T (B^T B) c
            = c^T S c.
            $$

            The energy numerator is

            $$
            \langle \phi \rvert H \lvert \phi \rangle
            = c^T (B^T H B) c
            = c^T H_{\mathrm{sub}} c.
            $$

            Minimizing the energy ratio

            $$
            \frac{c^T H_{\mathrm{sub}} c}{c^T S c}
            $$

            leads to the generalized eigenvalue problem

            $$
            H_{\mathrm{sub}} c = E S c.
            $$

            Once we solve for $c$, the reconstruction step

            $$
            \lvert \psi_{\mathrm{SQD}} \rangle = B c
            $$

            means that each coefficient in $c$ tells us how much of each selected basis vector is used in the final approximate state.
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
        code_cell(
            """
            state_probability_comparison_df = pd.DataFrame(
                {
                    "bitstring": basis_labels,
                    "exact_probability": np.abs(exact_ground_state) ** 2,
                    "sqd_probability": np.abs(sqd_state) ** 2,
                }
            ).sort_values("exact_probability", ascending=False, ignore_index=True)

            state_probability_comparison_df
            """
        ),
        code_cell(
            """
            ideal_indices = support_df.head(top_k)["bitstring"].map(lambda bitstring: basis_labels.index(bitstring)).tolist()
            B_ideal = np.eye(len(basis_labels))[:, ideal_indices]
            H_ideal = B_ideal.T @ H @ B_ideal
            S_ideal = B_ideal.T @ B_ideal
            ideal_energy = eigh(H_ideal, S_ideal)[0][0]

            ideal_comparison_df = pd.DataFrame(
                {
                    "case": ["exact full solve", "sample-chosen reduced basis", "ideal top-support reduced basis"],
                    "energy": [exact_ground_energy, sqd_energy, ideal_energy],
                }
            )
            ideal_comparison_df["absolute_error"] = abs(ideal_comparison_df["energy"] - exact_ground_energy)

            ideal_comparison_df
            """
        ),
        markdown_cell(
            r"""
            ### Why compare probabilities of the exact and reconstructed states

            Energies are important, but they do not show the full shape of the state.

            This table gives a more visual intuition:

            - the exact column shows where the true ground state lives,
            - the SQD column shows where the reconstructed reduced-space state lives.

            If the important rows match reasonably well, then the reduced basis is not only reproducing one number, it is capturing the structure of the state itself.
            """
        ),
        markdown_cell(
            r"""
            ### Why the ideal reduced-basis comparison is useful

            This extra comparison helps separate two different effects:

            - **projection error**: the error caused by working in a smaller space at all,
            - **sampling error**: the error caused by choosing that space from finite noisy samples.

            The ideal reduced-basis row says, "What if we had picked the top support perfectly?" Comparing that row to the sampled row tells you how much the sampling stage itself is helping or hurting.
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

            An overlap close to $1$ means the approximate state points in almost the same direction as the exact ground state.

            Beginners often focus only on the energy, but the overlap is extremely useful because it tells us whether the approximate vector itself is faithful, not just whether one scalar number happened to come out close.

            Here is the mathematical logic of these two metrics:

            $$
            \text{energy error} = |E_{\mathrm{SQD}} - E_0|
            $$

            measures how far the approximate energy is from the exact ground-state energy, while

            $$
            \text{state overlap} = |\langle \psi_0 \vert \psi_{\mathrm{SQD}} \rangle|
            $$

            measures how aligned the two state vectors are.

            So one metric compares **numbers**, and the other compares **directions in vector space**.

            If both states are normalized, then the overlap behaves like a cosine between vectors:

            $$
            0 \le |\langle \psi_0 \vert \psi_{\mathrm{SQD}} \rangle| \le 1.
            $$

            Values close to $1$ mean the vectors point in almost the same direction, while smaller values mean the approximate state is pointing away from the exact one.
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
            ### How to judge whether the reduced problem worked

            A good SQD result usually has two features at the same time:

            - a small energy error,
            - a large state overlap.

            If the energy looks good but the overlap is poor, that can still mean the reduced subspace is missing important structure. So it is healthy to inspect more than one metric whenever possible.
            """
        ),
        markdown_cell(
            r"""
            ### A plain-language summary of the comparison step

            At this point, you should be able to say something very concrete:

            - We solved the big problem exactly.
            - We solved a smaller sampled version approximately.
            - We measured how close those two answers are.

            That is the core scientific question of the notebook. Everything that follows is about understanding **when** that approximate answer becomes more reliable and **why** it can fail.
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

            This section answers a very practical beginner question:

            **If I change the amount of data or the size of the reduced basis, how should the approximation respond?**

            The experiment gives us a more trustworthy answer than one lucky run because it averages over many random trials.

            Very loosely, the sampling error in empirical probabilities tends to shrink as the number of shots increases, so we expect

            $$
            \hat{p}(x) \to p(x)
            \quad \text{as} \quad
            N \to \infty.
            $$

            The notebook does not prove a full convergence theorem, but it does let you see the practical consequence of this idea numerically.
            """
        ),
        markdown_cell(
            r"""
            ### What the helper function below will do

            Before you run the code, it helps to know the role of the helper function:

            - it performs one full SQD trial for a chosen shot count and subspace size,
            - it returns the absolute energy error for that one trial,
            - we then repeat that process many times and average the errors.

            So the function is basically a compact way of saying:

            "Repeat the sample-based workflow under one chosen setting, and report how far the reduced answer is from the exact one."
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
        code_cell(
            """
            experiment_pivot_df = experiment_df.pivot(
                index="shots",
                columns="subspace_size",
                values="mean_abs_energy_error",
            )

            experiment_pivot_df
            """
        ),
        markdown_cell(
            r"""
            ## Step 12: Visualize the convergence trend

            We expect the energy error to improve when:

            - we collect more shots, because the empirical distribution better matches the true one,
            - we allow a slightly larger subspace, because we reduce the chance of excluding an important basis state.

            The plot below helps us see that trend instead of guessing it from a table.

            When you read the figure, do not look only for a perfectly smooth curve. Sampling is noisy, so the important question is whether the overall direction is improving as the resources increase.
            """
        ),
        markdown_cell(
            r"""
            ### Why the pivot table is useful before the plot

            The pivoted table is a compact summary:

            - each row fixes the number of shots,
            - each column fixes the subspace size,
            - each entry tells you the mean absolute energy error.

            Some learners find tables easier to reason about first and plots easier to interpret second. Keeping both views makes the convergence story easier to digest.
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

            This is worth seeing because beginners sometimes think the reduced diagonalization step itself is magically fixing everything. It is not. The quality of the reduced answer depends strongly on the quality of the chosen subspace.

            Symbolically, if the exact state has important weight outside the chosen subspace, then

            $$
            \lvert \psi_0 \rangle \notin \operatorname{span}\{\text{chosen basis states}\},
            $$

            and the projected solve cannot reproduce the exact ground state perfectly, no matter how accurately we diagonalize inside that reduced space.
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
        code_cell(
            """
            failure_comparison_df = pd.DataFrame(
                {
                    "case": ["exact ground state", "good sampled subspace", "bad chosen subspace"],
                    "energy": [exact_ground_energy, sqd_energy, bad_energy],
                }
            )
            failure_comparison_df["absolute_error"] = abs(failure_comparison_df["energy"] - exact_ground_energy)

            failure_comparison_df
            """
        ),
        markdown_cell(
            r"""
            ### Why the failure table matters

            This table puts three situations next to each other:

            - the exact answer,
            - the SQD answer from the informative sampled subspace,
            - the answer from a deliberately poor subspace.

            Seeing those side by side makes the logic of SQD very concrete: the quality of the reduced diagonalization depends strongly on whether the reduced basis actually contains the important physics.
            """
        ),
        markdown_cell(
            r"""
            ## Step 14: What this notebook should leave you with

            The full SQD workflow is now visible:

            1. Solve or estimate a state whose measurements reveal important basis states.
            2. Sample bitstrings from that state.
            3. Keep the configurations that appear important.
            4. Build a reduced basis matrix $B$.
            5. Form $H_{\mathrm{sub}} = B^T H B$ and $S = B^T B$.
            6. Solve the reduced eigenvalue problem.
            7. Check whether the answer converges as you increase shots or enrich the subspace.

            In larger chemistry or materials problems, the same logic is used, but the state preparation, symmetry constraints, and Hamiltonian construction become more sophisticated.

            The core lesson stays the same:

            $$
            \text{good samples} \longrightarrow \text{good subspace} \longrightarrow \text{good reduced diagonalization}.
            $$

            In very compact mathematical language, the notebook compares:

            $$
            \text{exact: } H \lvert \psi_0 \rangle = E_0 \lvert \psi_0 \rangle
            $$

            with

            $$
            \text{reduced: } H_{\mathrm{sub}} c = E S c, \qquad \lvert \psi_{\mathrm{SQD}} \rangle = B c.
            $$

            If you only remember one sentence from this notebook, let it be this:

            **SQD does not guess the answer out of nowhere. It uses samples to decide where the important part of the full quantum problem probably lives, and then solves the physics inside that smaller region.**
            """
        ),
        markdown_cell(
            r"""
            ## A few common beginner pitfalls to watch for

            Before you leave the notebook, here are some easy mistakes to avoid when you revisit the workflow on your own:

            1. Do not confuse **amplitudes** with **probabilities**. The probabilities come from squared magnitudes.
            2. Do not assume a small energy error automatically means the approximate state is perfect. Check overlap too when you can.
            3. Do not forget that the subspace comes from data. If the data are poor, the projected solve can only do so much.
            4. Do not treat the reduced basis as arbitrary. The entire SQD idea depends on choosing it intelligently from the samples.

            If those points are clear, then you have understood the main logic of the method.
            """
        ),
        markdown_cell(
            r"""
            ## Try it yourself

            If you want to turn this notebook from something you read into something you truly understand, try these small experiments:

            1. Change the random seed and see whether the selected sampled bitstrings stay the same.
            2. Lower the shot count and watch how the sampling table and final errors change.
            3. Increase `top_k` and see how the reduced-basis dimension affects the approximation.
            4. Print the exact and SQD probabilities again after your changes and compare their support.

            Those tiny experiments are often the fastest way to build intuition, because they force you to connect the mathematics to the behavior of the code.
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
