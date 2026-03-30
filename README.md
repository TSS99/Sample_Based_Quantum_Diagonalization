# Sample-Based Quantum Diagonalization

This repository is a beginner-friendly walkthrough of sample-based quantum diagonalization (SQD).

If you are new to the topic, the short version is this:

- a Hamiltonian matrix $H$ contains the energy information of a quantum system,
- diagonalizing $H$ gives us its eigenvalues and eigenstates,
- for large systems, full diagonalization becomes too expensive,
- SQD uses samples to guess which basis states matter most and then solves a smaller problem inside that reduced space.

The project is written for someone who wants more than a quick demo. The notebook explains the full workflow slowly, in plain language, and with enough mathematics to make every step precise.

You can think of SQD as a two-part idea: first use samples to discover where the important physics seems to live, then solve the smaller problem inside that discovered region.

The main teaching resource is the notebook:

- `notebooks/sample_based_quantum_diagonalization_workflow.ipynb`

The notebook builds the SQD idea from first principles:

1. Start from a small Hamiltonian.
2. Solve the full problem exactly so we have a reference answer.
3. Turn the target eigenstate into a sampling problem.
4. Reconstruct a small subspace from the observed bitstrings.
5. Project the Hamiltonian into that subspace.
6. Solve a much smaller eigenvalue problem.
7. Compare the SQD estimate against the exact answer.

The goal is not only to run code, but to understand why each step works mathematically, what information enters at each stage, and how the final reduced diagonalization connects back to the original quantum problem.

## Quick start

Clone the repository and move into the project folder:

```bash
git clone https://github.com/TSS99/Sample_Based_Quantum_Diagonalization.git
cd Sample_Based_Quantum_Diagonalization
```

Create the virtual environment and install the required libraries:

```bash
./setup_env.sh
```

This script creates `.venv`, installs the packages from `requirements.txt`, and registers a Jupyter kernel for the project.

Activate the environment whenever you return to the project:

```bash
source .venv/bin/activate
```

Launch JupyterLab:

```bash
./start_notebook.sh
```

## What the notebook teaches

The notebook is written for a reader who may be new to both quantum computing and numerical diagonalization.

It explains:

1. What an eigenvalue problem is in the language of quantum mechanics.
2. Why full diagonalization becomes expensive as the Hilbert space grows.
3. How measurement samples tell us which computational basis states matter most.
4. How to build a reduced subspace from those samples.
5. Why the reduced problem can be solved with a projected Hamiltonian.
6. When SQD succeeds and when it fails.

## Tiny glossary before you begin

If some of the words below feel unfamiliar, keep this section nearby while reading the notebook.

- **Hamiltonian**: the matrix that represents the energy structure of the system.
- **Eigenvalue**: a special number $E$ such that $H \lvert \psi \rangle = E \lvert \psi \rangle$.
- **Eigenstate**: the state $\lvert \psi \rangle$ that belongs to that eigenvalue.
- **Ground state**: the eigenstate with the smallest eigenvalue.
- **Basis state**: one of the simple reference states used to describe all other states. In this notebook the basis states are bitstrings such as $000$ and $101$.
- **Amplitude**: the coefficient in front of a basis state in a quantum superposition.
- **Born rule**: the rule that turns an amplitude into a measurement probability through $|a_x|^2$.
- **Subspace**: a smaller vector space inside the full Hilbert space.
- **Projection**: the act of restricting a large matrix problem to a smaller chosen subspace.

## Workflow at a glance

The notebook follows the same sequence every time:

1. Define a Hamiltonian matrix $H$.
2. Solve $H \lvert \psi \rangle = E \lvert \psi \rangle$ exactly for a reference answer.
3. Convert the ground-state amplitudes into sampling probabilities with the Born rule.
4. Draw bitstring samples that imitate repeated measurements.
5. Keep the most important sampled configurations.
6. Form the projected Hamiltonian $H_{\mathrm{sub}} = B^T H B$.
7. Form the overlap matrix $S = B^T B$.
8. Solve the reduced problem $H_{\mathrm{sub}} c = E S c$.
9. Rebuild the approximate state in the full Hilbert space.
10. Compare the approximate energy with the exact one.

## How to read the notebook

The notebook is designed to be read from top to bottom without skipping.

The best way to use it is:

1. Read each markdown cell slowly before running the next code cell.
2. Pause after every table or plot and ask what changed mathematically.
3. Compare the exact answer and the SQD answer instead of treating them as unrelated outputs.
4. Rerun the sampling sections with a different random seed or shot count to build intuition.

If you are completely new, do not worry about memorizing everything on the first pass. The important thing is to follow the chain of logic from:

exact state $\rightarrow$ sampled bitstrings $\rightarrow$ reduced basis $\rightarrow$ projected Hamiltonian $\rightarrow$ approximate energy.

## What you should expect to see while running it

If the notebook is working correctly, you should see all of the following along the way:

1. A printed Hamiltonian table indexed by three-bit basis states.
2. A table of exact eigenvalues and a clearly identified ground-state energy.
3. A support table showing which bitstrings carry the most probability.
4. A measurement-count table built from finite sampling.
5. A reduced-basis selection based on the most frequent sampled bitstrings.
6. A projected Hamiltonian and overlap matrix.
7. A comparison between the exact answer and the SQD approximation.
8. A convergence plot showing how error changes with shots and subspace size.

That sequence is helpful because it lets you match every mathematical idea to a concrete output.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── setup_env.sh
├── start_notebook.sh
├── notebooks/
│   └── sample_based_quantum_diagonalization_workflow.ipynb
└── scripts/
    └── generate_sqd_notebook.py
```

## A note about the example

The notebook uses a small three-qubit Hamiltonian on purpose.

That is not because SQD only matters for small problems. It is because small problems are the best place to learn the workflow carefully:

- you can see the full Hamiltonian,
- you can inspect every basis state,
- you can verify the exact answer,
- you can see how sampling changes the result.

Once the workflow feels natural on a toy model, it becomes much easier to understand how the same structure scales to chemistry, materials, or larger fermionic systems.

## GitHub rendering note

The markdown in this repository uses GitHub-friendly math delimiters such as `$...$` and `$$...$$` so the equations render more reliably in both the README and the notebook preview on GitHub.

## Regenerating the notebook

If you edit the generator script, recreate the notebook with:

```bash
python3 scripts/generate_sqd_notebook.py
```

You can also scan the repo for GitHub-unfriendly math delimiters with:

```bash
python3 scripts/check_github_math.py
```
