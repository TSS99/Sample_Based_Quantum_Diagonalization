# Sample-Based Quantum Diagonalization

This repository is a beginner-friendly walkthrough of sample-based quantum diagonalization (SQD).

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

The goal is not only to run code, but to understand why each step works mathematically.

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

Activate the environment whenever you return to the project:

```bash
source .venv/bin/activate
```

Launch JupyterLab:

```bash
./start_notebook.sh
```
