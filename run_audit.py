#!/usr/bin/env python3
"""Verify every Table 2 instance and separate supplemental constructions."""
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from guardband.core import Case,Construction,audit_case,clique_check


def run(output,export):
    output.mkdir(parents=True,exist_ok=True)
    rows=json.loads((ROOT/'data/fixtures/positive_cases.json').read_text())['cases']
    results=[]
    for row in rows:
        case=Case.from_dict(row)
        result=audit_case(case,output/'assignments'/case.id if export else None)
        results.append(result)
        print(f"{case.id:31} {result['status']} V={result['vertices']} E={result['edges']} minimum gaps={result['min_vertex_vertex_gap']},{result['min_edge_edge_gap']},{result['min_vertex_edge_gap']} failures={result['total_failures']}",flush=True)
    witnesses=[clique_check(d,2*d+1) for d in range(2,7)]
    assert all(w['valid'] for w in witnesses)
    (output/'lee_clique_witnesses.json').write_text(json.dumps(witnesses,indent=2)+'\n')
    # Reconcile all Table 2 rows with the actual proof hypotheses and tested fixtures.
    with (ROOT/'data/fixtures/table2.csv').open(newline='') as f: table=list(csv.DictReader(f))
    actual=[r for r in results if r['group']=='table2']
    checks=[]
    for row,r in zip(table,actual):
        d,u,n,m,L,kap=(int(row[x]) for x in ('d','u','n','m','chi_1_1_u','kappa_d'))
        k=d*(d+1); w=witnesses[d-2]
        valid=(d,u,n,m,L)==(r['d'],r['u'],r['n'],r['m'],r['palette']) and d>=2 and n>=2*d+1 and m>=2*d+1 and L==2*k+2*u-1 and 2<=u and 2*u<=kap+1<=k and kap==w['witness_cardinality'] and (d*n)%L==0 and ((d+1)*m)%L==0 and r['status']=='PASS'
        # The lower bound is from Corollary 1; the audit checks its hypotheses,
        # not the nonexistence of every smaller-palette coloring by search.
        checks.append(dict(row,case_id=r['id'],clique_lower_bound=L,construction_upper_bound=L,hypotheses_and_coloring_valid=valid))
    if len(table)!=8 or len(actual)!=8 or not all(x['hypotheses_and_coloring_valid'] for x in checks):
        raise RuntimeError('Table 2 reconciliation failed')
    with (output/'table2_verified.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=checks[0].keys(),lineterminator="\n");w.writeheader();w.writerows(checks)
    summary={}
    for group in ('table2','supplemental'):
        selected=[r for r in results if r['group']==group]
        summary[group]={'cases':len(selected),'passed':sum(r['status']=='PASS' for r in selected),**{f:sum(r[f] for r in selected) for f in ('vertices','edges','directed_edge_evaluations','edge_edge_comparisons','total_failures')}}
    (output/'results.json').write_text(json.dumps({'summary':summary,'cases':results},indent=2)+'\n')
    flat=[{k:v for k,v in r.items() if k!='failures'} for r in results]
    with (output/'results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=flat[0].keys(),lineterminator="\n");w.writeheader();w.writerows(flat)
    print(json.dumps(summary,sort_keys=True),flush=True)
    return int(any(r['status']!='PASS' for r in results))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'data/generated');ap.add_argument('--export-assignments',action='store_true');a=ap.parse_args();sys.exit(run(a.output,a.export_assignments))
