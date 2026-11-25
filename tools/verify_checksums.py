#!/usr/bin/env python3
"""Verify all SHA-256 entries in SHA256SUMS.txt from repository root."""
import hashlib
import pathlib
import sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
manifest=ROOT/'SHA256SUMS.txt'
if not manifest.is_file():
    raise SystemExit('Missing SHA256SUMS.txt')
errors=[]
lines=manifest.read_text(encoding='utf8').splitlines()
for line in lines:
    if not line.strip():continue
    expected,filename=line.split('  ',1)
    file=ROOT/filename
    if not file.is_file():errors.append(f'MISSING: {filename}');continue
    actual=hashlib.sha256(file.read_bytes()).hexdigest()
    if actual!=expected:errors.append(f'MISMATCH: {filename}')
print(f'Checked {len(lines)} files: ', 'PASS' if not errors else 'FAIL')
for e in errors:print(e)
sys.exit(1 if errors else 0)
