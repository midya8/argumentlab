# Attack-switch sensitivity

[Live inspector](https://midya8.github.io/argumentlab/switches.html) · [Core semantics and six inspected sources](METHOD.md)

## Scope

This extension fixes the argument set and chosen semantics. The input supplies a baseline framework, up to six distinct attack pairs that may be toggled, and one query. At most six arguments and 64 configurations are allowed. These bounds are tighter than the original eight-argument inspector because every configuration requires a complete subset audit. It is a finite inspection tool, not a new or scalable enforcement solver.

Input has exactly `framework`, `switches`, `query`. The framework follows the base strict graph schema. Switches are distinct valid pairs, including self attacks; pairs may be present or absent at baseline. Query has exactly `semantics`, `mode`, `argument`, `value`. Semantics is one of the nine base families. Modes are `exists`, `credulous`, `skeptical_classical`, `skeptical_nonvacuous`. Value must be a boolean. Exists requires a null argument; other modes require one valid argument, so only exists queries apply to the empty framework.

Framework attacks and switch pairs are canonical sorted. Bit i of configuration mask m toggles sorted switch i. Thus `R_m = R_0 symmetric_difference {switch_i | bit_i(m)=1}`. No other attack changes and no argument is added or removed. Flips are the popcount of m, exactly the symmetric-difference attack distance because every pair occurs once. No weight, plausibility, utility or real-world cost is assigned.

## Exact queries and minimality

Each configuration runs the complete core audit. It retains the chosen full family record and acceptance witnesses/counterexamples for every argument, every family extension list and every subset's nine classifications, defended mask and range. Selecting a configuration in the browser recomputes its full core audit independently of native retained JSON. That full audit includes conflicts, every defense response, all strict-superset/range witnesses, complete labelling legality and grounded steps. The CLI's `--configuration-mask` option similarly returns the full selected audit alongside sensitivity. Separate browser exports preserve sensitivity and selected-audit schemas without implying the sensitivity export contains every full core witness for every configuration.

Exists is family nonemptiness. Credulous and classical skeptical queries use the base quantifiers. Nonvacuous skeptical uses the base product field: when no extension exists it is null, not false. Null matches neither boolean query target. This is an explicit nullable interface convention, not the literature's two-valued non-empty skeptical predicate, which is false if the family is empty. The inspector does not treat classical vacuous truth as concrete acceptance or count absent-family null as negative nonvacuous acceptance.

A configuration succeeds exactly when its answer is the requested boolean. All successful masks are retained. Minimum flips is the least popcount of a successful mask; every tied minimum survives. With no solution, minimum is null and both minimum/inclusion-minimal solution lists are empty. A successful mask is inclusion-minimal iff none of its proper bit-subsets succeeds. Every proper successful subconfiguration is retained as its minimality witness. Inclusion-minimal solutions can use more edits than a minimum-cardinality solution. If baseline already succeeds, mask 0 is the unique inclusion-minimal and minimum-cardinality solution, although other masks may also succeed.

Every edit-count layer lists all masks and partitions answers into true, false and null, plus all matches. Every hypercube edge starts with switch i unset and sets just that switch. There are `k*2^(k-1)` edges for k>0 and zero for k=0. Edges retain old/new answers, exact gained/lost chosen-family extension masks and addition/removal relative to baseline. These edges are descriptive input differences, not estimated causal effects. No monotonicity or pruning assumption is used.

## Original strict controls

The retained minimal-vs-minimum control has baseline attacks0→1,2→2, preferred credulous acceptance of a1, and switches1→0,1→1,2→0,2→2 after canonical sorting. Successful masks are1,5,9,12,13. The unique minimum is mask1 (one added reverse attack), while inclusion-minimal masks are1 and12 (two edits). Mask12 adds2→0 and removes2→2. Every proper subconfiguration of12 fails. This is a statement about these supplied hypothetical inputs, not a recommendation to alter an argument.

A separate seeded original control retains a strict comparable chain of configurations where acceptance is lost and regained. The full input, every answer and all intermediate cube edges are retained rather than asserting global monotonicity from one example. Three-cycle stable existence has all three tied one-flip solutions1,2,4; locked self attacks, no-switch success/impossibility, empty frameworks, classical-vs-nullable vacuity, mixed additions/removals, every semantics and a six-switch/six-argument full cube complete the 21 controls. No source example or benchmark generator was copied.

## Checks and reproduction

All 19 native and five Node/Chrome base tests remain. Combined CI runs 32 Python test functions on 3.10-3.13 and ten Node/actual-Chrome tests. New native checks replay every one of 256 two-argument baseline/switch-set pairs, all 72 semantics/mode/target combinations, 80 seeded larger cases and all 21 retained reports. An independently set-based family oracle checks each resulting graph; separate replay reconstructs symmetric differences, every query, full classifications, all proper successful subconfigurations, minimum ties, layers and every cube edge. CLI checks include invalid-output preservation and full selected-audit equality.

Four new Node engine tests compare 256 complete sensitivity reports on 154,485 scalar leaves, 21 retained reports on 84,739 leaves, and another 152 full reports from all query combinations plus 80 additional seeded systems. Native/JavaScript sensitivity enumeration and bookkeeping are separate implementations; both reuse their own independently implemented base semantics engines. Thus these are independent cross-language implementations, not two novel semantics algorithms. These descriptive counts are not timing or solver-quality benchmarks.

The new actual-Chrome suite checks all 209 retained configurations, all 5,205 subset/defense records, 802 per-family argument acceptance cards, 423 single-switch transitions, every summary/tile/classification/layer/full selected native-audit comparison, tile selection, both exports, invalid/stale clearing and all 21 controls at 320/390/1280. Tiles have at least44px dimensions and page containment is checked. Supplementary wide tables own labelled horizontal scroll. The six-switch cube is fully enumerated; testing has no special exemption for dense controls.

Isolated installed-wheel checks reproduce 19 base and 21 switch reports outside the checkout, verify five imported module origins belong to site-packages, reconstruct all 209 configuration graphs, and compare both console/module CLI forms, including a full selected audit. CI regenerates both fixture files and examples byte-for-byte. Base JSON fixtures stay unchanged.

```sh
python -m pip install .
argumentlab-switches examples/switches.json --configuration-mask 3
python -m argumentlab.switches examples/switches.json --output /tmp/switch-report.json
python -m unittest discover -s tests -v
PYTHONPATH=. python tools/build_switch_audits.py
npm test
sh tools/wheel_smoke.sh
python -m http.server 8000 --directory docs
```

Open `/switches.html`. Native parse bounds 65,536 UTF-8 bytes and rejects duplicate JSON keys. Browser bounds65,536 characters and uses JSON.parse's last duplicate key. Native rejects lexical float count/endpoints; JavaScript accepts numerically integral safe values. Both validators reject boolean count/endpoints, duplicate switches/attacks, unknown fields/modes, out-of-bound masks and unsupported graph sizes. The native direct structure API has no text-length bound. These are the same explicitly documented parser distinctions as base, not an identical-parser claim.

## Additional inspected dynamics sources

The original six sources in METHOD.md still own the nine static semantics and complete labelling rules. Three additional sources were fetched and their relevant sections inspected:

- Ringo Baumann, Sylvie Doutre, Jean-Guy Mailly and Johannes P. Wallner, *Enforcement in Formal Argumentation*, Journal of Applied Logics, volume8 issue6 (2021). Introduction, section2.2 definition2.4, section3.1 general setup/definition3.1 and section3.2.3 definition3.18 inspected: https://helios2.mi.parisdescartes.fr/~jmailly/downloads/enforcement_ifcolog.pdf . Establishes dynamics/enforcement as prior work, precise acceptance/existence distinctions, allowed changes and symmetric-difference distance. We specialize to a supplied bounded local switch cube and one argument/existence query, not the full framework of enforcement operators. The nullable product mode is distinguished from its two-valued non-empty skeptical predicate.
- Sylvie Coste-Marquis, Sebastien Konieczny, Jean-Guy Mailly and Pierre Marquis, *Extension Enforcement in Abstract Argumentation as an Optimization Problem*, IJCAI2015. Abstract/introduction, argument-fixed definition4 and minimal-change encoding discussion inspected: https://www.ijcai.org/papers15/Papers/IJCAI15-407.pdf . Fixed arguments with editable attacks and minimal attack changes are established ideas. No pseudo-Boolean encoding, solver code, source example, experiment or scalability claim was copied. Our single-argument acceptance queries are not presented as the paper's full strict/non-strict extension enforcement.
- Andreas Niskanen, Johannes P. Wallner and Matti Jarvisalo, *Pakota: A System for Enforcement in Abstract Argumentation*, JELIA2016. Abstract/introduction and section2.3 status enforcement inspected: https://www.cs.helsinki.fi/u/andreasn/papers/niskanenwj-jelia2016.pdf . Status enforcement and minimum symmetric-difference attack changes are prior work; stable skeptical enforcement explicitly requires a stable extension. We do not copy Pakota, its SAT/MaxSAT/CEGAR algorithms, input format, generators or benchmarks, nor claim equivalent scope/performance or affiliation. Classical and nullable product modes are visibly separate here.

## Limits

Failure means no matching configuration inside the supplied switches, not that unrestricted enforcement is impossible. A minimum is relative to the unit switch count, not the best/wisest/cheapest real-world action. The arguments and attacks are formal assumptions. This does not model evidence, persuasion, strategic choices, morality, truth, probabilities or causal effects. No new theory, solver, complexity result, scalability or machine-checked correctness claim. Original implementation, independent checks and synthetic controls: Midya Rahmani.
