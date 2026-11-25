@echo off
cd /d "%~dp0"
python tools/verify_checksums.py || exit /b 1
python run_pairing_audit.py --output reproduced || exit /b 1
python run_audit.py --export-assignments --output reproduced || exit /b 1
python verify_exports.py --input reproduced || exit /b 1
python -m unittest discover -s tests -v || exit /b 1
python tools/compare_reproduction.py --input reproduced || exit /b 1
