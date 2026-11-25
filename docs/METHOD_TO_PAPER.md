# Mapping to the current manuscript

| Mathematical statement | Implementation and verification |
|---|---|
| Lemma 1 | `core.lee_phase`, `lee_steps`, `validate_lee_interval`: local phase values exactly −K,…,−1,1,…,K. |
| Lemma 2 | `Construction.phase`, `offset`, `color_vertex`, `color_edge`, `opposite_offset_ok`: period closure and reversal; numerical audit of integer gaps. |
| Lemma 3 | Lower-bound proof in manuscript; not a computational chromatic-number solver. |
| Lemma 4 / Corollary 1 | `clique_witness`, `clique_check`; Table 2 hypotheses verified by `run_audit.py`. |
| Theorem 1 | `pairings.exact_modular` independently searches all modular rows; `proof_pairs` follows ordinary or endpoint/near-Skolem construction; `validate_modular` checks partition and all congruences. |
| Remark 1 | Proof certificates for obstructed class contain exactly one wrapped pair; general exact-cover witnesses need not use the same decomposition. |
| Corollary 2 | `Construction(family='saturated')` uses L=Δ+2u−1, φ=λ mod L, ω(z_h)=b_h, ω(−z_h)=a_h; excluded cases are fixed-phase obstructions only. |
| Proposition 1 | `family='upper'`: M=Δ+2u, ordinary/hooked Skolem positions translated by u−1. |
| Theorem 2 / Table 2 | `table2.csv`, eight saturated cases, full assignments, `table2_verified.csv`. Exact value follows analytically from Corollary 1 + construction. |
| §5.1 / Table 1 | `proof_k6_u3.json` preserves the literal six pairs; mod 17, wrapped difference 6. |
| §5.2 | `family='guard2'`: Q=Δ+3, φ=4λ, ω=2λ. |
| Theorem 3 | `family='odd'`: Q0=Δ+1, φ=2λ, ω=λ. `family='cover'`: M=Δ+2, p=K+1, palette 2p−1; within-layer midpoint, cross-layer p+[j−i]_p−1. |
| Corollary 3 | `transpose=True` swaps coordinates in the linear phase and closure, not in the underlying graph definition. |
| Corollary 4 | Scale all labels by s; target palette s(R−1)+1; u=max(1,ceil(t/s)) in the fixtures. |
| Section 7 | `run_pairing_audit.py`, `run_audit.py`, `verify_exports.py`, `tests/`. |

## Exact-cover representation

The columns represent K required differences and 2K interval positions. For each ordered pair (a,b) with b−a≡h (mod L), add a row with three covered columns. Translate positions by −u during independent search, then restore them in certificates. A search state is the set of uncovered columns; the active rows are exactly those disjoint from covered columns, so caching failed states is sound. For L−K>2K−1 no wrapped candidate row exists; these identical matrices can be reused without applying a parity criterion. All 90 results are compared to Theorem 1 only after the search.

Proof-structured certificates are distinct from independent exact-cover witnesses. For the wrapped case, q=2u, (a_q,b_q)=(L−u,u); the remaining pairs have ordinary differences and partition the interior interval. The certificate loader validates these features. For the ordinary case all differences are positive integers. The Table 1 certificate is copied literally from the current manuscript. Neither the proof-based search nor the optional bounded search is asserted to be a polynomial-time generator.

## Limits

The graph family requires n,m≥2d+1. Every construction enforces its own period condition. The `upper` modulus is not a substitute for `saturated` closure, and fixed-phase failure is not a lower bound for arbitrary colorings. The package tests finite cases only; it does not establish novelty, classify all periods or prove Theorem 2 by exhaustion.
