"""Exact-integer constructions and audits for the current manuscript."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from collections import defaultdict
from pathlib import Path
from typing import Any
import csv
import json
from .pairings import proof_pairs, upper_pairs, validate_modular

CERTIFICATE_DIR = Path(__file__).resolve().parents[2] / 'data' / 'certificates'


def lee_phase(d: int, step: tuple[int, int]) -> int:
    a, b = step
    return d*a + (d+1)*b


def lee_steps(d: int) -> list[tuple[int, int]]:
    if d < 1:
        raise ValueError('Radius d must be a positive integer')
    return [(a,b) for a in range(-d,d+1) for b in range(-d,d+1)
            if 0 < abs(a)+abs(b) <= d]


def validate_lee_interval(d: int) -> bool:
    k = d*(d+1)
    values = sorted(lee_phase(d,z) for z in lee_steps(d))
    return values == list(range(-k,0)) + list(range(1,k+1))


def modular_certificate(k, u):
    path = CERTIFICATE_DIR / f'proof_k{k}_u{u}.json'
    if path.is_file():
        data = json.loads(path.read_text(encoding='utf-8'))
        if (data['K'],data['u']) != (k,u) or len(data['pairs']) != k:
            raise ValueError('Certificate metadata mismatch')
        pairs = {row['h']:(row['a'],row['b']) for row in data['pairs']}
        validate_modular(pairs,k,u)
        if k%4 in (0,1):
            if any(b-a!=h for h,(a,b) in pairs.items()):
                raise ValueError('Ordinary proof certificate has wrapped pair')
        else:
            q=2*u; L=2*k+2*u-1
            if pairs.get(q)!=(L-u,u) or any(b-a!=h for h,(a,b) in pairs.items() if h!=q):
                raise ValueError('Incorrect endpoint/near-Skolem certificate')
        return pairs
    return proof_pairs(k,u)


@dataclass(frozen=True)
class Case:
    id: str
    family: str
    d: int
    n: int
    m: int
    u: int
    palette: int
    r: int = 1
    s: int = 1
    t: int = 1
    group: str = 'supplemental'
    transpose: bool = False

    @classmethod
    def from_dict(cls, row: dict[str,Any]) -> 'Case':
        return cls(**row)

    def as_dict(self) -> dict[str,Any]:
        return dict(vars(self))


class Construction:
    def __init__(self, case: Case):
        self.c = case
        d=case.d
        if any(not isinstance(q,int) for q in (d,case.n,case.m,case.u,case.palette,case.r,case.s,case.t)):
            raise ValueError('All construction parameters must be integers')
        if d<1 or case.n < 2*d+1 or case.m < 2*d+1:
            raise ValueError('Both periods must be at least 2d+1')
        if case.s < 1 or not (0 <= case.r <= case.s) or case.t < 0:
            raise ValueError('Require s>=1, 0<=r<=s, t>=0')
        self.k = d*(d+1)
        self.degree = 2*self.k
        self.steps = lee_steps(d)
        if len(self.steps) != self.degree or not validate_lee_interval(d):
            raise AssertionError('Lee local interval does not check out')
        self.family = case.family
        self.pairs = None
        self.vfactor = None
        f = case.family
        if f == 'cover':
            p = self.k+1
            self.modulus = 2*p
            self.base_palette = 2*p-1
            self.vfactor = 1
            self.base_guard = 1
        elif f == 'odd':
            self.modulus = 2*self.k+1
            self.base_palette = self.modulus
            self.vfactor = 2
            self.base_guard = 1
        elif f == 'guard2':
            self.modulus = 2*self.k+3
            self.base_palette = self.modulus
            self.vfactor = 4
            self.base_guard = 2
            if case.u != 2:
                raise ValueError('guard2 construction requires u=2')
        elif f in ('saturated','upper'):
            self.vfactor = 1
            self.base_guard = case.u
            self.modulus = 2*self.k+2*case.u-(f=='saturated')
            self.base_palette = self.modulus
            self.pairs = modular_certificate(self.k,case.u) if f=='saturated' else upper_pairs(self.k,case.u)
        else:
            raise ValueError(f'Unknown construction family: {f}')
        if case.u < 1:
            raise ValueError('This release implements only u>=1 construction families')
        if self.base_guard * case.s < case.t:
            raise ValueError(f'Scaling provides guard {self.base_guard * case.s}, less than requested t={case.t}')
        target=(self.base_palette-1)*case.s+1
        if case.palette != target:
            raise ValueError(f'Palette mismatch for {f}: expected {target}, received {case.palette}')
        pn,pm=(case.m,case.n) if case.transpose else (case.n,case.m)
        if ((self.vfactor*d*pn) % self.modulus or
            (self.vfactor*(d+1)*pm) % self.modulus):
            raise ValueError('Period closure fails for the selected phase and modulus')

    def linear(self, x: tuple[int,int]) -> int:
        return lee_phase(self.c.d,x[::-1] if self.c.transpose else x)

    def phase(self, x: tuple[int,int]) -> int:
        return self.vfactor*self.linear(x) % self.modulus

    def color_vertex(self,x:tuple[int,int])->int:
        if self.family=='cover':
            return (self.phase(x) % (self.k+1)) * self.c.s
        return self.phase(x)*self.c.s

    def offset(self,step:tuple[int,int])->int:
        h=self.linear(step)
        if h==0 or abs(h)>self.k:
            raise ValueError('Not a nonzero Lee generator')
        if self.family=='odd':
            return h % self.modulus
        if self.family=='guard2':
            return 2*h % self.modulus
        if self.family in ('saturated','upper'):
            a,b=self.pairs[abs(h)]
            return b if h>0 else a
        raise ValueError('Covering formula is not a phase-offset table')

    def color_edge(self,x:tuple[int,int], step:tuple[int,int])->int:
        if self.family=='cover':
            y=((x[0]+step[0])%self.c.n,(x[1]+step[1])%self.c.m)
            a,i=divmod(self.phase(x),self.k+1)
            b,j=divmod(self.phase(y),self.k+1)
            p=self.k+1
            if a==b:
                # Within one layer, midpoint in Z_p (p odd).
                return (((i+j)*pow(2,-1,p))%p)*self.c.s
            # Cross-layer: unique layer-zero endpoint is the reference.
            if a==0:
                return (p+((j-i)%p)-1)*self.c.s
            return (p+((i-j)%p)-1)*self.c.s
        return ((self.phase(x)+self.offset(step)) % self.modulus)*self.c.s

    def opposite_offset_ok(self) -> bool | None:
        if self.family == 'cover':
            return None
        return all((self.offset(z)-self.offset((-z[0],-z[1]))-
                    self.phase(z)) % self.modulus == 0 for z in self.steps)


def audit_case(case:Case, export_dir:Path|None=None) -> dict[str,Any]:
    """Audit all vertices, all directed arcs and every incident-edge pair.

    Every difference uses ordinary integer representatives, not cyclic distance.
    Returns six independent integer failure counters plus observed minima.
    """
    c=Construction(case)
    n,m=case.n,case.m
    failures={name:0 for name in ('orientation','cardinality','range','vertex_vertex','edge_edge','vertex_edge')}
    adj=defaultdict(list)
    edge_records={}
    vertex_rows=[]
    vv_min=ve_min=ee_min=None
    def minof(current:int|None,value:int)->int:
        return value if current is None or value<current else current
    for x0 in range(n):
        for x1 in range(m):
            x=(x0,x1)
            vertex_color=c.color_vertex(x)
            vertex_rows.append((x0,x1,c.phase(x),vertex_color))
            if not 0<=vertex_color<case.palette:
                failures['range']+=1
            for step in c.steps:
                y=((x0+step[0])%n,(x1+step[1])%m)
                key=(x,y) if x<y else (y,x)
                label=c.color_edge(x,step)
                if key in edge_records:
                    if edge_records[key]['edge_color']!=label:
                        failures['orientation']+=1
                    edge_records[key]['reverse_color']=label
                else:
                    other_vertex=c.color_vertex(y)
                    edge_records[key]={'step':step,'edge_color':label,
                                       'reverse_color':None,'source_vertex_color':vertex_color,
                                       'target_vertex_color':other_vertex}
                    if not 0<=label<case.palette:
                        failures['range']+=1
                    diff=abs(vertex_color-other_vertex)
                    vv_min=minof(vv_min,diff)
                    if diff<case.r:
                        failures['vertex_vertex']+=1
                ve_gap=abs(vertex_color-label)
                ve_min=minof(ve_min,ve_gap)
                if ve_gap<case.t:
                    failures['vertex_edge']+=1
                adj[x].append(label)
    expected_edges=n*m*c.degree//2
    if len(edge_records)!=expected_edges or len(adj)!=n*m or any(len(v)!=c.degree for v in adj.values()):
        failures['cardinality']+=1
    if any(rec['reverse_color'] is None for rec in edge_records.values()):
        failures['cardinality']+=1
    comparisons=0
    for colors in adj.values():
        for a,b in combinations(colors,2):
            comparisons+=1
            diff=abs(a-b)
            ee_min=minof(ee_min,diff)
            if diff<case.s:
                failures['edge_edge']+=1
    expected_comparisons=n*m*c.degree*(c.degree-1)//2
    if comparisons != expected_comparisons:
        failures['cardinality']+=1
    result={
        'id':case.id,'group':case.group,'family':case.family,'d':case.d,'u':case.u,
        'n':n,'m':m,'r':case.r,'s':case.s,'t':case.t,'modulus':c.modulus,
        'palette':case.palette,'transpose':case.transpose,'degree':c.degree,'vertices':n*m,'edges':len(edge_records),
        'directed_edge_evaluations': n*m*c.degree,
        'edge_edge_comparisons':comparisons,
        'min_vertex_vertex_gap':vv_min,'min_edge_edge_gap':ee_min,
        'min_vertex_edge_gap':ve_min,
        'opposite_offset_identity': c.opposite_offset_ok(),
        'failures': failures,'total_failures':sum(failures.values()),
        'status': 'PASS' if not sum(failures.values()) else 'FAIL'
    }
    if export_dir is not None:
        export_dir.mkdir(parents=True,exist_ok=True)
        with (export_dir/'vertices.csv').open('w',newline='',encoding='utf-8') as fh:
            writer=csv.writer(fh,lineterminator="\n")
            writer.writerow(['x','y','phase_residue','vertex_color'])
            writer.writerows(vertex_rows)
        with (export_dir/'edges.csv').open('w',newline='',encoding='utf-8') as fh:
            writer=csv.writer(fh,lineterminator="\n")
            writer.writerow(['vertex1_x','vertex1_y','vertex2_x','vertex2_y',
                             'step_from_vertex1_dx','step_from_vertex1_dy',
                             'edge_color_from_vertex1','edge_color_from_vertex2',
                             'vertex1_color','vertex2_color'])
            for (a,b),rec in sorted(edge_records.items()):
                writer.writerow([*a,*b,*rec['step'],rec['edge_color'],
                                 rec['reverse_color'],rec['source_vertex_color'],
                                 rec['target_vertex_color']])
        with (export_dir/'local_offsets.csv').open('w',newline='',encoding='utf-8') as fh:
            writer=csv.writer(fh,lineterminator="\n")
            writer.writerow(['step_dx','step_dy','lee_phase',
                             'phase_shift_modulo','offset_modulo_or_blank'])
            for z in c.steps:
                writer.writerow([*z,c.linear(z),c.phase(z),
                                 '' if c.family=='cover' else c.offset(z)%c.modulus])
        (export_dir/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result


def clique_witness(d:int)->list[tuple[int,int]]:
    """Explicit Lee-diameter-d witness, as used for the lower bound."""
    if d<1:raise ValueError('d>=1')
    def ball(center:tuple[int,int],rad:int):
        a,b=center
        return {(a+x,b+y) for x in range(-rad,rad+1) for y in range(-rad,rad+1)
                if abs(x)+abs(y)<=rad}
    if d%2==0:
        pts=ball((0,0),d//2)
    else:
        h=(d-1)//2
        pts=ball((0,0),h) | ball((1,0),h)
    return sorted(pts)


def clique_check(d:int,period:int|None=None)->dict[str,Any]:
    pts=clique_witness(d)
    count=len(pts)
    diameter=max(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in combinations(pts,2))
    if period is not None:
        if period<2*d+1:raise ValueError('period at least 2d+1')
        norm=lambda a,b: min(abs(a[0]-b[0]),period-abs(a[0]-b[0]))+min(abs(a[1]-b[1]),period-abs(a[1]-b[1]))
        if any(norm(a,b)>d for a,b in combinations(pts,2)):
            raise AssertionError('Witness is not a clique on torus')
    # All d>=1: even 2h => 2h(h+1)+1; odd 2h+1 => 2(h+1)^2.
    expected = ((d*d+2*d+2)//2) if d%2==0 else ((d+1)*(d+1)//2)
    return {'d':d,'witness_cardinality':count,'expected_cardinality':expected,
            'max_integer_lee_distance':diameter,'valid':count==expected and diameter<=d,
            'vertices':[list(z) for z in pts]}
