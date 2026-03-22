#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name sample-based-quantum-diagonalization --display-name "Python (SQD)"

echo
echo "Environment is ready."
echo "Activate it with: source .venv/bin/activate"
