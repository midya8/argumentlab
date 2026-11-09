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
