"""Exact cover and constructive reductions in manuscript Theorem 1."""
from functools import lru_cache


def theorem1(k, u):
    if k < 1 or u < 1:
        raise ValueError('K,u must be positive')
    return k % 4 in (0, 1) or 2*u <= k


@lru_cache(maxsize=256)
def _solve(positions, differences, modulus=None):
    """Exact cover by minimum remaining values; memoize failed subproblems."""
    n = len(positions)
    if n != 2*len(differences):
        raise ValueError('Position count must be twice difference count')
    index = {a:i for i,a in enumerate(positions)}
    rows, masks = [], []
    cols = [0]*(n+len(differences))
    for j,h in enumerate(differences):
        for a in positions:
            b = a+h if modulus is None else (a+h)%modulus
            if b not in index or b == a:
                continue
            mask = (1<<index[a]) | (1<<index[b]) | (1<<(n+j))
            bit = 1<<len(rows)
            rows.append((h,a,b)); masks.append(mask)
            for c in (index[a], index[b], n+j):
                cols[c] |= bit
    conflicts=[]
    for mask in masks:
        c=mask; union=0
        while c:
            b=c&-c; union |= cols[b.bit_length()-1]; c-=b
        conflicts.append(union)
    dead=set()
    def search(uncovered, active):
        if not uncovered: return ()
        if uncovered in dead: return None
        remaining=uncovered; options=0; best=len(rows)+1
        while remaining:
            bit=remaining&-remaining; remaining-=bit
            candidates=cols[bit.bit_length()-1]&active
            count=candidates.bit_count()
            if count<best:
                best=count; options=candidates
                if best==0: break
        while options:
            bit=options&-options; options-=bit
            i=bit.bit_length()-1
            tail=search(uncovered^masks[i], active&~conflicts[i])
            if tail is not None: return (rows[i],)+tail
        dead.add(uncovered)
        return None
    return search((1<<len(cols))-1,(1<<len(rows))-1)


def exact_modular(k,u):
    """Independent decision by exact cover; no theorem/parity shortcut."""
    if k<1 or u<1: raise ValueError('K,u must be positive')
    L=2*k+2*u-1
    # Translate I to [0,2K-1]. If no wrapped row can exist, reuse the
    # identical ordinary candidate matrix across different moduli.
    mod = L if L-k <= 2*k-1 else None
    result=_solve(tuple(range(2*k)),tuple(range(k,0,-1)),mod)
    if result is None: return None
    return {h:(a+u,b+u) for h,a,b in result}


def validate_modular(pairs,k,u):
    L=2*k+2*u-1
    if set(pairs)!=set(range(1,k+1)):
        raise ValueError('Missing or unexpected difference')
    if sorted(p for ab in pairs.values() for p in ab)!=list(range(u,L-u+1)):
        raise ValueError('Pairs do not partition I')
    if any((b-a)%L!=h for h,(a,b) in pairs.items()):
        raise ValueError('Incorrect modular difference')


def proof_pairs(k,u):
    """Theorem 1 construction, ordinary or exactly one wrapped endpoint.

    The classical sequence component is found by exact cover. Runtime is
    not bounded uniformly; the theorem is the existence proof.
    """
    if not theorem1(k,u): raise ValueError('Theorem 1 excludes this fixed-phase pairing')
    L=2*k+2*u-1
    if k%4 in (0,1):
        result=_solve(tuple(range(1,2*k+1)),tuple(range(k,0,-1)))
        if result is None: raise RuntimeError('Ordinary Skolem search failed')
        pairs={h:(a+u-1,b+u-1) for h,a,b in result}
    else:
        q=2*u
        result=_solve(tuple(range(1,2*k-1)),tuple(h for h in range(k,0,-1) if h!=q))
        if result is None: raise RuntimeError('Near-Skolem search failed')
        pairs={h:(a+u,b+u) for h,a,b in result}
        pairs[q]=(L-u,u)
    validate_modular(pairs,k,u)
    return pairs


def upper_pairs(k,u):
    """Proposition 1 ordinary/hooked construction; one unused offset."""
    positions=tuple(range(1,2*k+1)) if k%4 in (0,1) else tuple(range(1,2*k))+ (2*k+1,)
    result=_solve(positions,tuple(range(k,0,-1)))
    if result is None: raise RuntimeError('Skolem/hooked search failed')
    pairs={h:(a+u-1,b+u-1) for h,a,b in result}
    M=2*k+2*u
    flat=[p for ab in pairs.values() for p in ab]
    if len(set(flat))!=2*k or not all(u<=p<=M-u for p in flat) or any(b-a!=h for h,(a,b) in pairs.items()):
        raise RuntimeError('Invalid upper-bound pairing')
    return pairs
