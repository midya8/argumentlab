# Ideal and eager: a shared position must defend itself

ArgumentLab0.4 is an original bounded inspector of established finite abstract-argumentation semantics. It does not introduce ideal/eager semantics or a new solver algorithm. Live entry: [core inspector](https://midya8.github.io/argumentlab/ideal.html).

## Contract

A request has exactly `arguments` (an integer0..8) and `attacks` (distinct directed index pairs, self attacks allowed). Every supplied edge is an assumption about attacks, not evidence of truth or strength. Strict validation rejects booleans in integer positions, extra keys, duplicate attacks, duplicate JSON object keys and noninteger numeric spellings at the CLI/browser parser. Generation accepts at most65,536 UTF-8 bytes; independent report replay accepts32MiB. Reports use integer bitmasks for positions, with argument a at bit a. Empty set is mask0.

For a position S, let F(S) contain the arguments whose every original attacker is attacked by a member of S. S is admissible when conflict-free and S ⊆ F(S). Preferred positions are inclusion-maximal admissible sets. Semi-stable positions are admissible positions with inclusion-maximal range S ∪ S⁺. This is inclusion, not cardinality or an arbitrary tie-break. All tied positions remain in the report.

For ideal, intersect all preferred positions; for eager, intersect all semi-stable positions. Each result is the greatest admissible subset of its intersection. The parent families are nonempty for these **finite** frameworks, including the zero-argument graph whose family is `[0]`, not `[]`. No arbitrary infinite-framework eager-existence or uniqueness claim is made.

## The descending trace, with outsiders retained

Write P for the parent intersection. Since P is conflict-free, iterate S₀=P and Sᵢ₊₁=Sᵢ ∩ F(Sᵢ) on the **original** graph. Each round removes all currently undefended members simultaneously. Every original attacker and every current defending response is retained. The final fixed point is admissible.

For any admissible T ⊆ P, induction gives T ⊆ Sᵢ: if T ⊆ Sᵢ, monotonicity gives T ⊆ F(T) ⊆ F(Sᵢ), so T survives the next round. Thus the terminal position contains every admissible subset of P and is the unique greatest one. Independently enumerating all such subsets and their union checks this argument on each supplied graph. At most n strict removals occur before the fixed-point record, but that bound does not make parent enumeration scalable.

Deleting attackers outside P is invalid: membership restriction is not graph restriction. A separate induced-pool grounded calculation and a single-pass calculation are **explicit wrong-shortcut contrasts**, not alternative definitions or accepted baselines.

## Original controls and the default cascade

`tools/ideal_cases.py` defines14 original synthetic controls, all531 directed graphs (loops included) on0..3 arguments, and100 seed72035 graphs on4..8 arguments. Contrast discovery used seed73041; the default is a discovered seven-argument cascade plus an isolated survivor a7. No research-paper example graph is copied.

Default preferred masks are156={a2,a3,a4,a7} and184={a3,a4,a5,a7}. Their intersection152={a3,a4,a7} is not admissible. First a4 has unanswered original attacker a0; removing it leaves a3 without a response to a6. The trace is152→136→128→128, ending at {a7}. One pass incorrectly leaves{a3,a7}; the induced-pool shortcut incorrectly keeps{a3,a4,a7}. Other controls distinguish grounded from ideal and ideal from eager, nonempty and empty cores, self attacks, odd cycles and the empty framework.

The report preserves every subset, conflicts, attacked/defended/range masks, all original attack responses, parent extensions, every admissible pool subset, maximal subsets, their union, every simultaneous trace state, each candidate's strict eligible supersets, per-argument parent membership and removal explanations. `inclusions` checks grounded ⊆ ideal ⊆ eager ⊆ the semi-stable intersection. These are set relations, not a universal ranking of semantics or people.

## Independent reproduction

```sh
python -m pip install .
argumentlab-ideal examples/ideal.json --output report.json
python -m argumentlab.ideal_cli report.json --verify
python -m unittest discover -s tests -v
node --test tests/test_ideal_engine.mjs tests/test_ideal_browser.cjs
sh tools/wheel_smoke.sh
# Optional external implementation, isolated environment recommended:
python -m pip install python-argumentation==2.0.2
PYTHONPATH=. python tools/check_ideal_pyarg.py
```

The native generator uses bitset admissibility. `ideal_verify.py` does **not** import it: it enumerates all3ⁿ complete ternary labellings, gets preferred parents from maximal in-sets and semi-stable parents from minimal undec-sets, and derives the unique maximal complete position inside each pool. Separate sets reconstruct all subset and pruning fields; exact recursive type checks reject bool/int substitutions and extra or missing fields. The complete-position characterization is supported by the primary sources below. This bounded replay is evidence, not a machine-checked proof of its implementation.

JavaScript uses sets and its own enumeration, loading no native reports. Tests compare645 full native/checker/JS reports,12,060 subset records and24,120 candidate obligations. A three-argument primitive-leaf mutation test rejects377 changed noninput leaves. Optional actual PyArg2.0.2 matches645 frameworks and1,290 ideal/eager families; it is a third-party reference, not an endorsement or a performance comparison. No PyArg source is vendored and it is not a runtime dependency.

Chrome tests exercise42 reports at1280/390/320 widths,84 core views,117 trace states,4,266 candidate selections and918 original-edge records. Fourteen downloads are triggered with real mouse input, awaited on disk and independently replayed. Installed-wheel tests run both entrypoints outside the source tree, inspect11 module origins, cover all14 ideal controls and reject20 selected forged CLI reports without replacing existing outputs. Existing core, switch and SCC workflows are retained.

## Inspected foundations and external reference

- Dung, Mancarella and Toni, *Computing ideal sceptical argumentation* (Artificial Intelligence,2007), Definition2.2, Lemma2.1 and Theorem2.1. Ideal sets are admissible subsets of every preferred extension; the ideal extension is greatest and complete. [Primary paper](http://cs.ait.ac.th/~dung/Site/Publications_files/ai07.pdf).
- Arieli and Caminada, *A general QBF-based formalization of abstract argumentation theory* (Journal of Applied Logic,2013). Finite extension/labelling formulations, including ideal/eager characterization. This inspector does not implement a QBF solver. [Primary paper](https://www2.mta.ac.il/~oarieli/Papers/jal13.pdf).
- van der Torre and Vesic, *The principle-based approach to abstract argumentation semantics* (2017), Definitions3.4/3.5. Complete ideal/eager formulations and the inclusion chain. [Published survey](https://orbilu.uni.lu/bitstream/10993/33989/1/ifcolog00017.pdf).
- Baumann and Spanring (2015), Theorem15. Eager uniqueness needs an existence condition for arbitrary infinite frameworks. This implementation stays finite. [Primary paper](https://dbai.tuwien.ac.at/staff/spanring/pub/BaumannSpanring2015.pdf).
- Baroni, Caminada and Giacomin, *Abstract argumentation frameworks and their semantics* (Handbook of Formal Argumentation,2018), early chapter's complete-labelling legality, Proposition3.21. Later ideal/eager sections were not used as evidence from the fetched excerpt. [Handbook chapter](https://users.cs.cf.ac.uk/CaminadaM/publications/HOFA_semantics.pdf).
- Borg and Odekerken, *PyArg: a tool for teaching and research in argumentation* (2022), inspected short demonstration, ideal/eager implementation coverage. [Demo paper](https://annemarieborg.nl/wp-content/uploads/2022/10/Borg-Odekerken_PyArg.pdf).
- PyArg2.0 documentation for framework construction, plus inspected installed2.0.2 ideal/eager modules and actual executions. [Documentation](https://daphneodekerken.github.io/PyArg/abstract_examples.html).

The library has exponential finite enumeration and a hard eight-argument boundary. It does not infer attacks, assess factual correctness, model probabilities, predict dialogue, compare solver speed or guarantee an AI agent's safety.
