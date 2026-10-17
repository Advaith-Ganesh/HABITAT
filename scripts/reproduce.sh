#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -m data.generate_dataset
.venv/bin/python -m ml.train
MPLCONFIGDIR="${TMPDIR:-/tmp}/habitat-mpl" .venv/bin/python -m ml.evaluate
MPLCONFIGDIR="${TMPDIR:-/tmp}/habitat-mpl" .venv/bin/python -m scripts.audit_v5
.venv/bin/python -m pytest -q
