#!/usr/bin/env python3
"""Section 7: independently decide all 90 modular exact-cover instances."""
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from guardband.pairings import exact_modular, theorem1, validate_modular


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    records=[]; certificates=[]
    for k in range(1,13):
        for u in range(1,k+2):
            pairs=exact_modular(k,u)
            found=pairs is not None
            expected=theorem1(k,u)
            if found:
                validate_modular(pairs,k,u)
                certificates.append({'K':k,'u':u,'L':2*k+2*u-1,'pairs':[{'h':h,'a':a,'b':b} for h,(a,b) in sorted(pairs.items())]})
            records.append({'K':k,'u':u,'L':2*k+2*u-1,'exact_cover_feasible':found,'theorem1_feasible':expected,'agreement':found==expected})
    summary={'cases':len(records),'feasible':sum(r['exact_cover_feasible'] for r in records),'infeasible':sum(not r['exact_cover_feasible'] for r in records),'disagreements':sum(not r['agreement'] for r in records)}
    with (output/'pairing_decisions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=records[0].keys(),lineterminator="\n");w.writeheader();w.writerows(records)
    (output/'pairing_certificates.json').write_text(json.dumps(certificates,indent=2)+'\n',encoding='utf-8')
    (output/'pairing_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True))
    return 0 if summary=={'cases':90,'feasible':63,'infeasible':27,'disagreements':0} else 1

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'data/generated');sys.exit(run(ap.parse_args().output))
