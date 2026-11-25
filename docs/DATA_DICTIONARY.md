# Data dictionary

All labels are ordinary integers in the declared consecutive palette 0,…,R−1. Modular phase residues and offsets are not themselves necessarily ordinary label gaps. CSVs are UTF-8, with header rows; JSON uses integer fields and boolean flags.

- `fixtures/table2.csv`: d, u, kappa_d (clique order), chi_1_1_u (paper exact value), n, m, result. Transcription of the eight manuscript rows.
- `fixtures/positive_cases.json`: case id, construction family, d,n,m,u,palette (length), requested r,s,t, group (`table2` or `supplemental`), transpose. For a scaled coloring, palette is s(R−1)+1.
- `certificates/proof_k*_u*.json`: K,u,pairs with h,a,b; actual interval residues, not raw Skolem positions. L=2K+2u−1.
- `generated/pairing_decisions.csv`: K,u,L, independent exact-cover feasibility, theorem feasibility, agreement. Infeasible entries have no witness; the exhaustive solver must be rerun for an independent decision.
- `generated/pairing_certificates.json`: one witness for each of 63 feasible decisions. These are independent exact-cover witnesses, not necessarily the proof-structured certificates above.
- `generated/pairing_summary.json`: totals of the 90 decisions.
- `generated/results.json` / `results.csv`: construction family, modulus, palette length, degree, vertex and edge counts, number of directed evaluations and incident-edge comparisons, minimum VV/EE/VE numerical gaps, reversal identity (null for quotient construction), failure counters and status. JSON includes counters by kind and summary by group; CSV flattens without nested counters.
- `generated/table2_verified.csv`: original Table 2 fields + case id, theoretical clique-based lower bound, verified construction upper bound, whether hypotheses and coloring pass. The lower bound is justified by the manuscript, not exhaustive coloring search.
- `generated/lee_clique_witnesses.json`: explicit lattice vertices, count, expected count, diameter and validity for d=2…6.
- `generated/assignments/<id>/vertices.csv`: x,y,phase_residue,vertex_color.
- `generated/assignments/<id>/edges.csv`: lexicographically ordered endpoints; unique Lee step from endpoint 1; edge label computed from each endpoint, and endpoint vertex colors. One row per undirected edge.
- `generated/assignments/<id>/local_offsets.csv`: step, linear phase (transposed if requested), phase residue, offset residue (blank for quotient cover).
- `generated/assignments/<id>/summary.json`: same case audit as results.json.

For each d,n,m, V=nm, Δ=2d(d+1), E=VΔ/2, directed evaluations=VΔ, and incident-edge comparisons=VΔ(Δ−1)/2. All three conflict types are checked using ordinary integer differences. Logs are actual runs of the included scripts; their formatting/runtime may vary.
