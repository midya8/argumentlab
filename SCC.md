# A cycle can split after a choice

ArgumentLab 0.3 adds an exhaustive SCC-recursive CF2/stage2 inspector beside the unchanged defense and attack-switch inspectors. [Open it](https://midya8.github.io/argumentlab/scc.html).

## What is computed

The input is exactly `{ "arguments": n, "attacks": [[a,b], ...] }`, with zero through six arguments, integer indices, no duplicate attacks and no extra fields. A mask selects argument `a` when bit `a` is set. Self attacks stay in the graph. This is CF2, not SCF2 with self-attacking arguments preprocessed away.

For every induced active argument set reached by the recursion, the report retains:

- The complete induced attack relation, reflexive reachability and SCC partition, ordered by lowest argument index.
- Every candidate subset, its conflicting edges, range, every strict conflict-free superset and every strict range-dominating conflict-free set.
- Global-to-that-subproblem naive/stage decisions and SCC-recursive CF2/stage2 decisions.
- For each candidate and each original SCC, all external selected attack edges, defeated arguments, surviving child graph, selected part, selected-but-removed arguments and both child membership results.

An argument is component-defeated when it is attacked by a selected argument outside its current SCC. For more than one SCC, restrict each original SCC by deleting these arguments and recursively test its selected part. Recompute SCCs inside every surviving child. At most one SCC is the base case: CF2 uses naive sets and stage2 uses stage sets. The empty graph has one empty extension, mask `[0]`, not an empty family. Naive means inclusion-maximal conflict-free; stage means inclusion-maximal range. Neither means maximum cardinality.

The implementation memoizes induced active masks, so the export is a shared subproblem DAG, not a chronological trace or a topological solver execution. Every candidate retains its own obligations, including failed ones. Child inspection preserves the selected part; if it selects a removed argument, there is no valid same-candidate selection and the button is disabled with a reason. All original argument indices are retained after deletion.

The root separately compares naive, global stage, CF2 and stage2 families, all containing/excluding extensions for every argument, existential credulous acceptance and universal skeptical acceptance. Set differences are contrasts, not a ranking of semantics.

## Original controls and exact contrasts

Fourteen original synthetic controls cover empty and isolated graphs, a source attack, a self-attacking source, an odd cycle, a six-cycle, deletion-induced splitting, a recursive deletion cascade, conditional external attack, global-stage/stage2 differences, disjoint cycles, all self attacks and opposite attack curves.

In the six-cycle, CF2 has masks `[9,18,21,36,42]` and stage2 has `[21,42]`: masks `[9,18,36]` are maximal conflict-free but do not have inclusion-maximal ranges. In control9, stage2 accepts mask `10` that global stage excludes. These do not establish that one semantics is universally better.

In the default cascade, selected mask `21` in the five-argument graph defeats argument1. Component mask `30` restricts to `28`, whose SCCs are `[4,8,16]`. Its preserved selected mask `20` then defeats argument3 in that new decomposition. Simply retaining the original SCC partition would hide the second deletion.

## Independent checks

`argumentlab.scc` generates with bitset transitive closure. `argumentlab.scc_verify` shares only structural input validation. It independently reconstructs every record using sets and graph searches, then checks every candidate's CF2/stage2 membership against a second published characterization: compute the least fixed point of component defeat, delete it, separate the remaining SCCs and test naive/stage membership, with the original global naive condition. It does not call the generator. Typed canonical JSON equality rejects missing/extra/reordered records, altered evidence and boolean-for-integer substitutions.

The JavaScript generator independently produces the same full schema. Cross-language checks cover all 531 directed graphs on zero through three arguments including loops, 180 seeded larger graphs and the14 controls: 725 reports, 3,052 induced subproblems, 16,375 candidate records and38,184 component obligations. These are coverage counts, not performance results.

The optional external comparison runs the unmodified ASPARTIX CF2 and stage2 encodings under clingo5.8.3 on the same531 small graphs,180 separately seeded larger graphs and14 controls. All725 frameworks and1,450 extension families agree. The encoding files are downloaded separately, hash-pinned and not vendored. It checks families, not our UI or every witness field. This is independent implementation agreement, not a proof of correctness.

Actual Chrome traverses all14 controls at320/390/1280:42 reports,171 subproblems,1,056 candidate selections,1,128 component obligations and3,780 repeated graph-edge states. It checks every report/node/candidate JSON record, tables, cards, acceptance family, selected/defeated nodes, attack geometry, child drill, stale clearing, recovery and page containment. Fourteen actual browser downloads are independently verified by Python. Wide candidate tables have their own horizontal scroll.

The full suite has39 Python test functions on3.10/3.11/3.12/3.13 and15 Node/Chrome tests. The isolated installed wheel checks19 defense reports,21 switch reports/209 configurations and14 SCC controls/14 rejected forgeries outside the checkout, seven module origins, both generation entrypoints and both verification entrypoints. Existing inspectors and reports remain covered.

## Reproduce

```sh
python -m pip install .
argumentlab-scc examples/scc.json --output /tmp/scc.json
python -m argumentlab.scc --verify /tmp/scc.json
python -m unittest discover -s tests -v
npm test
sh tools/wheel_smoke.sh
python -m http.server 8000 --directory docs
```

Optional external check, requiring network access only for these explicit reference downloads:

```sh
mkdir -p /tmp/argumentlab-reference
curl -fL https://www.dbai.tuwien.ac.at/research/argumentation/aspartix/dung/cf2.dl -o /tmp/argumentlab-reference/cf2.dl
curl -fL https://www.dbai.tuwien.ac.at/research/argumentation/aspartix/dung/stage2_gringo.lp -o /tmp/argumentlab-reference/stage2_gringo.lp
python -m pip install clingo==5.8.3
PYTHONPATH=. python tools/check_scc_aspartix.py --encoding-dir /tmp/argumentlab-reference
```

Expected SHA256: CF2 `ac02cb1bc64a86400982b09b49c5a8d9cdc774b6402fb17f632be29a2c0404d9`; stage2 `4c61429ba3d86f8a8ac0cbab4a7c0c64ec27c743c816744820373bc887526d00`. The script refuses changed files. clingo is optional, never a runtime dependency or required CI dependency.

## Inspected foundations and precise use

1. Sarah A. Gaggl and Stefan Woltran, *cf2 Semantics Revisited*, COMMA2010, primary paper. Definitions of component defeat, SCC recursion, restricted reachability and the least fixed point underpin the two independent checking paths: https://iccl.inf.tu-dresden.de/w/images/3/30/Cf2_semantics_revisitedGW.pdf . No source code or examples copied.
2. Wolfgang Dvorak and Sarah A. Gaggl, *Incorporating Stage Semantics in the SCC-recursive Schema for Argumentation Semantics*, NMR2012, primary paper. Definitions2-10 and the fixed-point/separation characterization distinguish global stage from stage2, including strict set inclusion: https://www.dbai.tuwien.ac.at/NMR12/proceedings/10_nmr12_paper10.pdf . No human-witness example or paper figure copied.
3. Wolfgang Dvorak and Sarah A. Gaggl, *Computational Aspects of cf2 and stage2 Argumentation Semantics*, COMMA2012, primary paper. Definitions and Proposition1 provide the global naive plus separated residual naive/stage characterization used by the independent verifier: https://iccl.inf.tu-dresden.de/w/images/7/7d/Comma2012_gaggl_dvorak.pdf . No complexity improvement claimed.
4. Pietro Baroni, Martin Caminada and Massimiliano Giacomin, *An introduction to argumentation semantics*, Knowledge Engineering Review26:4,2011, survey. Established naive/stage distinctions and SCC-recursive setting, not an empirical ranking: https://bista.sites.dmi.unipg.it/didattica/CSP/argumentation/KER-BaroniCaminadaGiacomin.pdf .
5. Federico Cerutti et al., *A SCC Recursive Meta-Algorithm for Computing Preferred Labellings in Abstract Argumentation*, KR2014, primary algorithm paper. Context for SCC decomposition and recomputation. Its preferred-labelling algorithm is not implemented or relabelled as CF2 here: https://orca.cardiff.ac.uk/89579/1/Cerutti-KR2014.pdf .
6. ASPARTIX, TU Wien, operator-maintained encoding registry and executable reference code: https://www.dbai.tuwien.ac.at/research/argumentation/aspartix/dung.html . The linked original [CF2 encoding](https://www.dbai.tuwien.ac.at/research/argumentation/aspartix/dung/cf2.dl) and [stage2 encoding](https://www.dbai.tuwien.ac.at/research/argumentation/aspartix/dung/stage2_gringo.lp) supply the external check. They remain separate downloads; their authorship is not ours.

## Limits and attribution

Six arguments, exhaustive subsets, no scalable/new solver claim. Supplied attacks are assumptions, not facts about truth, reliability, debate winners or persuasion. No structured argument construction, human evaluation, causal result, machine-checked proof, universally best semantics or new theorem. Native generation bounds UTF-8 input at65,536 bytes and verification at4MiB, rejects duplicate keys/nonfinite constants and writes output atomically. Browser input bounds UTF-8 bytes but uses JSON.parse's last-key convention; JavaScript cannot distinguish integral `1.0` from `1`. Accepted normalized inputs are compared, not falsely claimed lexically identical parsers.

Original bounded implementation, independent checks, interface and synthetic controls: Midya Rahmani. Published semantics and external encodings belong to the cited authors. MIT license for this repository's original code.
