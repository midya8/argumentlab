# ArgumentLab: defense, not a vote

[Live inspector](https://midya8.github.io/argumentlab/) · [Method and six inspected sources](METHOD.md)

An exact, finite abstract-argumentation inspector. Given arguments and directed attacks, inspect every subset's conflicts and defense responses, then compare nine extension families. Independent Python bitsets and JavaScript sets agree on complete computational witnesses. No model, API or private dataset.

## What it makes visible

- Every attacker and every selected defender, including unanswered attackers and self attacks.
- Conflict-free, admissible, complete, naive, preferred, stable, semi-stable, stage and grounded families, with every tie retained.
- All strict admissible/conflict-free supersets and range-dominance witnesses. Inclusion-maximal is not maximum cardinality.
- The full grounded characteristic-function chain and every complete three-valued labelling's local legality.
- Credulous and classical skeptical acceptance, every containing/excluding extension, first witnesses/counterexamples, and explicit empty-family conventions.
- Directed graph with separate opposite-attack curves, self loops and selected-set highlighting; all tables, full JSON and export remain inspectable.

Original strict controls show a smaller preferred extension can coexist with a larger one, preferred intersection can exceed grounded and can even fail admissibility, and stage can differ from semi-stable. These distinguish definitions rather than rank a universally best semantics.

## Do not miss the empty-family distinction

For a self-attacking argument, no stable extension exists. Classical skeptical acceptance is vacuously true because no extension excludes the argument. That does not mean a position accepts it: credulous acceptance is false. The separate `skeptical_nonvacuous` field is null and `exists` is false. The interface shows a warning. By contrast, a zero-argument framework has one empty extension `[0]`, not an empty family `[]`.

## Reproduce

```sh
python -m pip install .
argumentlab examples/demo.json --output /tmp/report.json
python -m argumentlab examples/demo.json
python -m unittest discover -s tests -v
PYTHONPATH=. python tools/build_audits.py
npm test
sh tools/wheel_smoke.sh
python -m http.server 8000 --directory docs
```

Open http://localhost:8000. Node22+ and Chrome are required for browser checks; `CHROME_BIN` can select Chrome. `uv` is needed for the isolated wheel check. The native CLI otherwise uses Python3.10+ with no runtime dependency. CI runs Python3.10-3.13 and regenerates the retained JSON exactly. The browser runs entirely locally after static assets load.

## Checks, not a benchmark

19 Python test functions cover every one of the 531 directed frameworks with zero through three arguments, including loops, plus 120 seeded larger frameworks, an independent set-based family oracle and exhaustive three-valued labelling enumeration. Witness replay checks every attacker/defender row, strict superset/range witness, acceptance quantifier and grounded step. Permutation, strict contrast, input/no-mutation and CLI checks are included.

Five Node/actual-Chrome tests compare all 531 full native reports on 344,023 exact scalar leaves and 19 retained controls on 152,884 leaves, plus 100 additional independent ternary-labelling controls. The retained controls contain 769 subsets, 171 family records, 576 per-family argument acceptance records, 39 complete labellings and 29 grounded steps. Actual Chrome checks every selected subset/family/labelling/step record, all tables and cards, graph edges/selected sets/path geometry, export and invalid/stale clearing. All 19 controls are checked for page containment at 320/390/1280. Repeated graph selections cover 19,622 edge states, not that many distinct supplied attacks. The installed wheel reproduces all 19 reports outside the checkout, verifies four module origins and compares console/module CLI output.

Counts describe original bounded controls and test coverage, not speed, solver quality or novel research.

## Honest limits

Eight arguments maximum, all subsets enumerated. Supplied attack relations are assumptions, not evidence about real-world truth, argument strength, debate winners or safe decisions. This uses established Dung semantics. No scalable/new solver, structured-argument construction, dialogue game, probability model, benchmark superiority or machine-checked proof claim. Native/browser JSON parser differences are documented in the method. Not affiliated with existing ArguLab or ARGTEACH systems; no external solver code, examples or datasets copied.

Original implementation, independent checks and synthetic controls: Midya Rahmani. MIT license.


## Attack-switch sensitivity extension

[Live edit-cube inspector](https://midya8.github.io/argumentlab/switches.html) · [Method and dynamics sources](SWITCHES.md)

Hold arguments and semantics fixed, supply at most six switchable attack pairs, then inspect every configuration. Retain all successful configurations, all tied minimum-edit matches and all inclusion-minimal matches, which can be larger. Every configuration keeps complete extension families, exact query witnesses and full subset classifications; every single-switch cube edge retains gained/lost extensions and old/new answers. Select a graph for its full defense, grounded and labelling audit.

Classical skepticism and nullable nonvacuous skepticism are distinct modes. A null nonvacuous answer matches neither true nor false. Original strict controls expose minimal-vs-minimum and acceptance loss/regain. Six arguments maximum, exhaustive enumeration, hypothetical supplied edits only: failure is relative to the allowed switches, not a general impossibility. No causal, strategic or new solver claim. Established enforcement research is attributed, not relabelled as original theory.

```sh
argumentlab-switches examples/switches.json --configuration-mask 3
python -m argumentlab.switches examples/switches.json --output /tmp/switch-report.json
PYTHONPATH=. python tools/build_switch_audits.py
```

All 19 original tests and five original Node/Chrome tests remain. Combined checks now run 32 Python tests on four versions and ten Node/actual-Chrome tests. New native checks cover every one of the 256 two-argument base-graph/switch-set pairs, all 72 semantics/mode/target combinations, 80 seeded larger systems and every retained control with an independent family oracle. Cross-language equality covers 256 full sensitivity reports, 21 retained reports and another 152 mode/seeded cases. The new browser suite checks all 209 configurations, 5,205 subset/defense records, 802 acceptance cards, 423 transitions and both exports, with all 21 controls at 320/390/1280. Installed wheel reproduces both original and switch reports, five module origins and both console/module CLIs. See the extension method for exact scalar counts and boundaries.

## SCC recursion: a cycle can split after a choice

[Open the CF2/stage2 inspector](https://midya8.github.io/argumentlab/scc.html) · [Exact contract, reproduction and inspected foundations](SCC.md)

Version0.3 adds a separate six-argument SCC-recursive inspector. Every candidate retains all component-defeat edges, restricted child graphs and child membership obligations. Recompute SCCs after deletion and drill into the surviving child with the selected part preserved. Compare global naive/stage against CF2/stage2 without treating them as a ranking. An independent set-based verifier checks every record and a second published fixed-point characterization; optional hash-pinned ASPARTIX/clingo checks agree on725 frameworks and1,450 extension families. Native/JavaScript full reports agree on725 frameworks,3,052 induced subproblems,16,375 candidates and38,184 obligations.

```sh
argumentlab-scc examples/scc.json --output /tmp/scc.json
python -m argumentlab.scc --verify /tmp/scc.json
```

The full suite now has39 Python functions on3.10-3.13 and15 Node/Chrome tests. New Chrome checks cover42 reports at320/390/1280,171 subproblems,1,056 candidate selections and14 actual independently verified downloads. The installed wheel reproduces19 defense,21 switch and14 SCC controls outside the checkout, checks seven module origins, rejects14 forged SCC reports and checks both generation and verification entrypoints. These are bounded coverage counts, not benchmark claims. Existing inspectors remain separate; published semantics/encodings are credited inSCC.md. No new theorem, scalable solver, human persuasion or universal-semantics ranking is claimed.
