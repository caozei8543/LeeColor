"""Compare all regenerated CSV/JSON evidence with the shipped release."""
from pathlib import Path
import argparse,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,default=ROOT/'reproduced');args=ap.parse_args()
original=ROOT/'data/generated'; expected={p.relative_to(original) for p in original.rglob('*') if p.is_file()}; actual={p.relative_to(args.input) for p in args.input.rglob('*') if p.is_file()}
errors=[]
for p in sorted(expected-actual):errors.append(f'Missing: {p}')
for p in sorted(actual-expected):errors.append(f'Unexpected: {p}')
for p in sorted(expected&actual):
    # Universal newlines make comparison portable to Windows.
    if (original/p).read_bytes().replace(b'\r\n',b'\n')!=(args.input/p).read_bytes().replace(b'\r\n',b'\n'):
        errors.append(f'Different: {p}')
print(f'Compared {len(expected)} evidence files: '+('FAIL' if errors else 'PASS'))
for e in errors:print(e)
sys.exit(bool(errors))
