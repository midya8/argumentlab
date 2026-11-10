# ArgumentLab method, provenance and limits

## Input and notation

An argumentation framework is a finite directed graph `(A,R)`. Attack `[a,b]` means a attacks b. Arguments are numbered `0..n-1`; `n` is an integer from zero through eight. Up to `n*n` distinct attack pairs are allowed. Self attacks are retained. Duplicate edges, unknown fields, non-integer/out-of-range endpoints and extra/missing fields are rejected. The normalized attack list is sorted; input order does not change a report. There are no argument weights, preferences or costs.

For `S ⊆ A`, `S+` is every argument attacked by a member of S. `F(S)` is every argument whose attackers are all attacked by S. An unattacked argument is defended by every S. The range is `S ∪ S+`. Masks are exact small integers: bit i represents argument ai. Integer mask order is only deterministic display order, not a preference or score.

## Exact family definitions

| Family | Definition |
|---|---|
| conflict_free | No attack has both endpoints in S, including self attacks. |
| admissible | Conflict-free and `S ⊆ F(S)`. |
| complete | Admissible and `S = F(S)`. |
| naive | Inclusion-maximal conflict-free set. |
| preferred | Inclusion-maximal admissible set. |
| stable | Conflict-free and range equals A. |
| semi_stable | Admissible and no admissible set has a strictly larger range by inclusion. |
| stage | Conflict-free and no conflict-free set has a strictly larger range by inclusion. |
| grounded | Least fixed point of F, obtained by iteration from the empty set. |

No maximality here means maximum cardinality. Equal ranges do not dominate each other. Every tied extension survives. Semi-stable can equivalently be characterized through range-maximal complete extensions; our independent native oracle uses that alternative while both production engines use admissible candidates.

Every subset retains its full list of internal attacks, attacked/defended/range masks, all argument defense records, all strict conflict-free/admissible supersets and all conflict-free/admissible range dominators. For every argument and attacker, the defense record lists all selected defenders and every unanswered attacker. These witnesses explain failures as well as successes.

Grounded iteration records the current set, full F(S), new members, full defense records and the final fixed step. Native checks confirm this fixed point belongs to every complete extension. The report checks stable ⊆ semi-stable ⊆ preferred ⊆ complete ⊆ admissible ⊆ conflict-free and stable ⊆ stage ⊆ naive ⊆ conflict-free. These are family inclusions, not claims that every pair in the diagram is equivalent.

## Labellings and acceptance

For a complete extension S, label S `in`, S+ `out`, and the remaining arguments `undec`. Each complete labelling retains every attacker's label and its local legality:

- In iff all attackers are out.
- Out iff at least one attacker is in.
- Undec iff there is no in attacker and there is at least one undec attacker.

Complete extensions and complete labellings have a bijection. Do not extend that claim to arbitrary admissible labellings, whose in-set mapping need not be injective. Tests independently enumerate every ternary assignment and apply these local rules without calling the production extension classifier.

For each family, credulous acceptance is membership in some extension; classical skeptical acceptance is membership in every extension. The report retains all containing and excluding extension masks and first witness/counterexample masks. Family union/intersection masks are exact, not probabilities or a voting rule.

An empty stable family has classical skeptical acceptance true for every argument by universal quantification, and credulous acceptance false. `exists=false`, separately named `skeptical_nonvacuous=null` and `intersection_nonvacuous_mask=null` prevent this formal vacuity from looking like a concrete accepted position. The classical empty-family intersection is A. This explicit convention matches the classical source below; the nullable field is an additional product view, not a replacement definition. A zero-argument framework has one empty extension under every family, so `exists=true` and each family is `[0]`, not `[]`.

## Original strict controls

- Three arguments with attacks 1→0, 1→2 and 2→1 have preferred masks2 (`{a1}`) and5 (`{a0,a2}`). Both are inclusion-maximal, only5 has maximum cardinality.
- Two arguments with self attack0 and attacks0→1,1→0 have grounded mask0 and preferred intersection mask2. Preferred skepticism is not grounded semantics.
- Four arguments with attacks0→1,0→3,1→0,1→3,3→2,3→3 have preferred intersection mask4 (`{a2}`), which is not admissible. An intersection of preferred extensions need not itself be a defensible position.
- Two arguments with self attack0 and attack0→1 have stage mask2 but semi-stable mask0. Stage need not defend its accepted argument.
- Odd/self cycles expose absent stable families; a seven-argument chain exposes multiple grounded steps. Empty, unattacked, disconnected, mutual/even-cycle and dense eight-argument limits are retained.

These synthetic controls were constructed locally, including a seeded search for strict contrasts, not transcribed from a source's examples. Simple graph motifs are established examples, not a novelty claim.

## Independent implementation and verification

Python production uses bitsets and per-target incoming attackers. JavaScript independently uses sets, outgoing-neighbor unions and set inclusion, with exact integers up to255. No native report is used during browser inference. The native oracle separately uses Python sets and alternative maximal-complete/range characterizations; full ternary enumeration independently checks complete labels and stable label absence of undec.

19 Python test functions run on3.10/3.11/3.12/3.13. Every directed graph with n=0,1,2,3, including loops, is checked: `1+2+16+512=531`. Another120 seeded n4..6 systems use independent family and complete-label oracles. Witness replay checks every argument response, every strict witness, all acceptance masks/quantifiers and every grounded step. Further controls exercise bounds, graph relabelling, input order, no mutation, invalid CLI output preservation and valid CLI serialization.

Five Node/Chrome tests include exact full-report equality over all531 systems/344,023 scalar leaves, 19 retained reports/152,884 leaves, 100 additional seeded n4..6 independent complete/stable ternary checks, strict validation/contrast/no-mutation checks and actual Chrome. Native JSON numbers and JavaScript arithmetic remain exact within these small masks; there is no floating-point probability or cost arithmetic.

The 19 retained reports contain769 subsets,171 family records,576 argument-acceptance records,39 complete labellings and29 grounded steps. Actual Chrome checks every selected record, every family/acceptance card, subset/defense/label table, full JSON, graph attack/source/target/selected-set correspondence and finite contained path geometry. Repeated selections inspect19,622 graph edge states, not distinct attacks. Export and stale/invalid clearing are tested. All19 controls are checked at320/390/1280 for page containment. Wide supplemental witness tables own their horizontal scroll; decision summaries/cards wrap within the main column.

An isolated installed wheel reproduces all19 reports outside the checkout, verifies four module origins point into site-packages and compares console/module CLI output. CI regenerates both retained JSON and demo input byte-for-byte. Readiness retries apply only before Chrome debugger discovery; inference assertions are never retried to pass.

### Parser and scope differences

Native `parse` bounds UTF-8 bytes at65,536 and rejects duplicate JSON keys. Browser input bounds JavaScript characters at65,536 and uses JSON.parse, which retains the last duplicate key. Native integer syntax rejects JSON float tokens such as `1.0`; JavaScript Number has no equivalent lexical distinction and accepts mathematically integral safe values. Both normalized structure validators reject booleans as endpoints/counts, non-integral/non-finite values, unknown fields, invalid endpoints and duplicate attacks. Direct native `audit(raw)` validates structure but has no text-length cap. These distinctions are documented rather than claimed to be byte-identical parsers. Reports match on accepted normalized controls.

## Inspected sources and precise use

1. Phan Minh Dung, *On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games*, Artificial Intelligence77 (1995),321-357. Primary paper, section2 definitions2,5,6,7,13,16,20,23; lemmas14,15,24 and theorem25 inspected. Source of abstract graphs, defense, original extension semantics, grounded fixed point and relevant inclusions: https://www.cs.ait.ac.th/~dung/Site/Publications_files/n-games.pdf . No game-theoretic/stable-marriage/default-logic translation implementation or experiments copied.
2. Pietro Baroni, Martin Caminada and Massimiliano Giacomin, *An introduction to argumentation semantics*, Knowledge Engineering Review26:4 (2011),365-410, DOI10.1017/S0269888911000166. Introduction and relevant section2 extension/labelling/legality definitions inspected: https://maxapress.com/data/article/ker/preview/pdf/S0269888911000166.pdf . Used to distinguish complete-label bijection from general admissible labellings and formal acceptance from argument truth. No survey examples copied.
3. Francesca Toni, *Argumentation frameworks for explanation-based reasoning*, KR2016 tutorial, Imperial College London. Slides7-15 inspected for exact extension definitions, distinct grounded/preferred-intersection semantics and complete-label iff rules: http://kr2016.cs.uct.ac.za/downloads/tutorials/Tutorial-Toni.pdf . No structured ABA/ASPIC/logic-program transformation or dialogue-game implementation claimed.
4. Guenther Charwat, Wolfgang Dvorak, Sarah A. Gaggl, Johannes P. Wallner and Stefan Woltran, *Methods for solving reasoning problems in abstract argumentation - A survey*, Artificial Intelligence220 (2015),28-63. Introduction/scope/background definitions1-6 inspected for naive, stage, semi-stable range definitions, complete labelling correspondence and reasoning queries: https://pmc.ncbi.nlm.nih.gov/articles/PMC4318991/ . No ArgSemSAT, ASPARTIX, ArguLab, SAT/CSP/ASP reduction, source code, benchmarks or performance results copied.
5. Sebastian Rudolph, TU Dresden Foundations of Knowledge Representation, *Abstract Argumentation*, lecture10, January8,2024. Semantics/query material, especially slide34, inspected for the explicit classical no-extension skeptical/credulous convention: https://iccl.inf.tu-dresden.de/w/images/4/44/Fkr-10-2024.pdf . The separate nonvacuous nullable field is our explicit interface addition, not attributed as a new semantics theorem.
6. Jeremie Dauphin and Claudia Schulz, *ARGTEACH - A learning tool for Argumentation Theory*, ICTAI2014, DOI10.1109/ICTAI.2014.120. Introduction/background/total complete-labelling rules inspected as established graphical/labelling educational precedent: https://icr.uni.lu/jeremiedauphin/downloads/ArgTeach.pdf . No interface, examples, code, partial-labelling hint algorithm or learning-outcome result copied. ArgumentLab is not affiliated with ARGTEACH or existing ArguLab systems.

## Boundaries

This is established finite abstract argumentation implemented for inspection. Every supplied attack is an assumption. Argument internals, evidence quality, preferences, support, uncertainty, argument generation and real-world consequences are outside the model. No new algorithm, scalability, benchmark superiority, calibrated probability, dialogue strategy, certified proof or machine-checked correctness claim. Original implementation, independent checks and synthetic controls: Midya Rahmani.

## SCC-recursive extension

Version0.3 adds a separate CF2/stage2 inspector with a smaller six-argument bound. Its complete schema, independent fixed-point verifier, original controls, optional published encoding comparison, parser differences, exact reproduction and inspected foundations are documented in [SCC.md](SCC.md). The defense and switch contracts above are preserved.
