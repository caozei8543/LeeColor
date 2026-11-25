#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
"$PYTHON" tools/verify_checksums.py
"$PYTHON" run_pairing_audit.py --output reproduced
"$PYTHON" run_audit.py --export-assignments --output reproduced
"$PYTHON" verify_exports.py --input reproduced
"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" tools/compare_reproduction.py --input reproduced
