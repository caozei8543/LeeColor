#!/usr/bin/env python3
"""Independent CSV-only verifier (does not import or call coloring constructors).

Checks all expected toroidal power edges against the exported edge CSV; all
vertex colors; both edge orientations; all 3 weighted gap types; and complete
degree/count information. It is intentionally separate from run_audit.py.
"""
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import csv
import json
import argparse
import sys

ROOT=Path(__file__).resolve().parent


def csv_dicts(path):
    with path.open(newline='',encoding='utf8') as file:
        return list(csv.DictReader(file))


def inspect(case,folder):
    n,m,d=case['n'],case['m'],case['d']
    expected_vertices=n*m
    deg=2*d*(d+1)
    values={}
    errors=[]
    for row in csv_dicts(folder/'vertices.csv'):
        xy=(int(row['x']),int(row['y']))
        color=int(row['vertex_color'])
        if xy in values or not (0<=xy[0]<n and 0<=xy[1]<m):
            errors.append('duplicate/invalid vertex '+str(xy))
        values[xy]=color
        if not 0<=color<case['palette']:
            errors.append('vertex palette range '+str(xy))
    if len(values)!=expected_vertices:
        errors.append('vertex count mismatch')
    if len(values)>0 and any((x,y) not in values for x in range(n) for y in range(m)):
        errors.append('missing vertex')
    neighbors=set()
    for x in range(n):
        for y in range(m):
            a=(x,y)
            for dx in range(-d,d+1):
                for dy in range(-d,d+1):
                    if 0<abs(dx)+abs(dy)<=d:
                        b=((x+dx)%n,(y+dy)%m)
                        neighbors.add((a,b) if a<b else (b,a))
    edge_data={}
    incident=defaultdict(list)
    for row in csv_dicts(folder/'edges.csv'):
        a=(int(row['vertex1_x']),int(row['vertex1_y']))
        b=(int(row['vertex2_x']),int(row['vertex2_y']))
        dx,dy=int(row['step_from_vertex1_dx']),int(row['step_from_vertex1_dy'])
        color=int(row['edge_color_from_vertex1'])
        reverse=int(row['edge_color_from_vertex2'])
        edge=(a,b)
        if a>=b or edge in edge_data:
            errors.append('noncanonical/duplicate edge '+str(edge))
        edge_data[edge]=color
        if 0<abs(dx)+abs(dy)<=d and ((a[0]+dx)%n,(a[1]+dy)%m)==b:
            pass
        else:
            errors.append('invalid stored Lee step '+str(edge))
        if edge not in neighbors:
            errors.append('invalid graph edge '+str(edge))
        if a not in values or b not in values:
            errors.append('missing endpoint '+str(edge))
            continue
        if int(row['vertex1_color'])!=values[a] or int(row['vertex2_color'])!=values[b]:
            errors.append('endpoint color mismatch '+str(edge))
        if color!=reverse:
            errors.append('orientation discrepancy '+str(edge))
        if not (0<=color<case['palette']):
            errors.append('edge palette range '+str(edge))
        if abs(values[a]-values[b])<case['r']:
            errors.append('vertex-vertex conflict '+str(edge))
        if abs(values[a]-color)<case['t'] or abs(values[b]-color)<case['t']:
            errors.append('vertex-edge conflict '+str(edge))
        incident[a].append(color)
        incident[b].append(color)
    if set(edge_data)!=neighbors:
        errors.append('complete edge set differs from independently enumerated torus')
    comparisons=0
    for v,colors in incident.items():
        if len(colors)!=deg:
            errors.append('degree mismatch '+str(v))
        for x,y in combinations(colors,2):
            comparisons+=1
            if abs(x-y)<case['s']:
                errors.append('edge-edge conflict '+str(v))
                if len(errors)>100:
                    return {'id':case['id'],'status':'FAIL','errors':errors[:100]}
    if len(incident)!=expected_vertices or len(edge_data)!=expected_vertices*deg//2:
        errors.append('degree/edge cardinality mismatch')
    if comparisons!=expected_vertices*deg*(deg-1)//2:
        errors.append('pair-comparison count mismatch')
    return {'id':case['id'],'status':'PASS' if not errors else 'FAIL',
            'vertices':len(values),'edges':len(edge_data),
            'incident_edge_pairs':comparisons,'errors':errors}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,default=ROOT/'data'/'generated')
    args=ap.parse_args()
    cases=json.loads((ROOT/'data/fixtures/positive_cases.json').read_text(encoding='utf8'))['cases']
    summaries=[]
    for case in cases:
        directory=args.input/'assignments'/case['id']
        if not directory.is_dir():
            print('MISSING DATA',directory,file=sys.stderr)
            return 2
        result=inspect(case,directory)
        summaries.append(result)
        print(f"{result['id']:<32} {result['status']}: V={result.get('vertices')} E={result.get('edges')} EE comparisons={result.get('incident_edge_pairs')}; {result['errors'][:3]}")
    total={'independent_export_check':'PASS' if all(c['status']=='PASS' for c in summaries) else 'FAIL',
           'cases':len(summaries),'total_edges':sum(r.get('edges',0) for r in summaries),
           'total_comparisons':sum(r.get('incident_edge_pairs',0) for r in summaries)}
    print('TOTAL',json.dumps(total,sort_keys=True))
    return 0 if total['independent_export_check']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
