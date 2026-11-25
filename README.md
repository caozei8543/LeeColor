# Exact [1,1,u]-colorings of toroidal grid powers via Lee cliques and modular difference pairings

**Reproducibility package v2.0.0**  
Manuscript authors: Weibiao Zhang and Tao Cao.

This package accompanies the manuscript with the title above. It provides source code, mathematical certificates, complete coloring assignments, and independent verification scripts for the computational checks reported in Tables 1–2 and Section 7, together with separately identified supplemental examples.

## Reproduce in one command

Python 3.10+; standard library only, no external solver or network required. Extract the archive and open a terminal in this directory.

```sh
bash run_all.sh
```

Windows: `run_all.bat` (or use the Python commands below).

```sh
python tools/verify_checksums.py
python run_pairing_audit.py --output reproduced
python run_audit.py --export-assignments --output reproduced
python verify_exports.py --input reproduced
python -m unittest discover -s tests -v
python tools/compare_reproduction.py --input reproduced
```

The scripts write fresh outputs to `reproduced/`, leaving shipped release evidence intact. Full exports require space for tens of MB of CSV files and memory for the largest torus (109 × 109, 499,002 undirected edges); running time depends on the machine. Avoid running multiple full audits concurrently. No fixed time guarantee is made. Run the checksum check before editing any tracked release file.

## What is reproduced

| Manuscript location | Computational evidence | Scope |
|---|---|---|
| Theorem 1 / Section 7 | `pairing_decisions.csv`, `pairing_certificates.json` | All 90 pairs of parameters: 1 ≤ K ≤ 12, 1 ≤ u ≤ K+1; 63 feasible, 27 infeasible, zero disagreements |
| Table 1 / §5.1 | `data/certificates/proof_k6_u3.json` | Exact six ordered pairs printed in the manuscript, including (14,3) at difference 6 |
| Lemma 4 / Corollary 1 | `lee_clique_witnesses.json`, `table2_verified.csv` | Explicit Lee-diameter cliques and arithmetic lower-bound hypotheses |
| Theorem 2 / Table 2 | `table2_verified.csv`, `results.csv`, complete CSV assignments | All eight rows, including d=5 and d=6 |
| Proposition 1, §5.2, Theorem 3, Corollaries 3–4 | Eight separately labeled supplemental cases | Representative upper-bound, total-coloring, transpose, direct and scaled constructions |

The exact-cover solver independently decides each modular instance before comparing with the theorem predicate. It searches rows covering one difference and two position columns, using the fewest-available-rows rule and memoized failed states. Identical nonwrapped candidate matrices may be reused across moduli; this is not a parity-based shortcut. Feasible cases include complete witnesses; infeasible decisions are exhaustive finite searches. Separately, the proof-based construction uses ordinary Skolem or endpoint wrapping plus a near-Skolem system, as in Theorem 1. The shipped larger certificates avoid costly searches in routine reproduction. `tools/regenerate_large_certificates.py` provides optional bounded seeded search; exhaustion does **not** imply infeasibility.

All graph audits check actual ordinary integer labels, both directions of each edge, both endpoint gaps, adjacent vertex labels and every incident-edge pair. `verify_exports.py` independently enumerates the toroidal graph and reads the CSV files without importing the constructors.

## Local verification results

| Group | Cases passed | Undirected edges | Directed evaluations | Incident-edge comparisons |
|---|---:|---:|---:|---:|
| Table 2 | 8/8 | 764,960 | 1,529,920 | 54,939,792 |
| Supplemental | 8/8 | 7,236 | 14,472 | 107,820 |
| Total | 16/16 | 772,196 | 1,544,392 | 55,047,612 |

All conflict counters were zero; independent CSV verification passed all 16 cases. The 13 unit tests passed, including a deliberately corrupted export rejection test. See the shipped logs.

## Mathematical and implementation boundaries

Let K=d(d+1), Δ=2K, λ(a,b)=da+(d+1)b. For saturated offsets L=2K+2u−1 and I={u,…,L−u}. The proof construction uses ω(z_h)=b_h and ω(−z_h)=a_h. For the fixed phase λ mod L, the existence condition in Corollary 2 is not a general nonexistence condition for arbitrary colorings. The one-label-larger bound uses its own modulus M=2K+2u and its own period closure. The ordinary total-coloring quotient uses modulus 2K+2 but palette 2K+1. These numbers must not be interchanged.

A finite feasible assignment proves an upper bound for the tested instance. Theorem 2 is exact because the paper proves the lower bound under the Lee-clique hypothesis, not because the code searches every smaller palette. The finite tests neither prove the infinite-family theorem nor establish novelty. The eight supplemental cases are not claimed to be experiments previously reported in Section 7. See [method mapping](docs/METHOD_TO_PAPER.md) and [data dictionary](docs/DATA_DICTIONARY.md).

## Repository structure

- `src/guardband/`: exact-cover, constructive reductions, phase/offset and graph audits.
- `data/fixtures/`: current Table 2 and graph-case parameters.
- `data/certificates/`: checked proof-structured pairings for all eight Table 2 instances.
- `data/generated/`: shipped run results, all vertex/edge assignments and local offsets.
- `logs/`: actual execution logs; `tests/`: automated unit and corruption checks.
- `tools/`: optional large-certificate regeneration, integrity check and output comparison.
- `.github/workflows/reproduce.yml`: GitHub Actions workflow for automated reproducibility checks.

This reproducibility package is released under the MIT License. See `LICENSE` for details. No unpublished manuscript is included. Please cite the accompanying manuscript and this software release using `CITATION.cff`.
