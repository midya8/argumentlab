"""Independent sets and exhaustive complete three-valued labellings.

Does not import ideal.py, its bitset enumeration or its pruning procedure.
"""

from itertools import product
from .ideal_input import validate, LIMITS


def expected(raw):
    framework = validate(raw)
    n = framework["arguments"]
    edges = list(map(tuple, framework["attacks"]))
    universe = set(range(n))
    sets = [{a for a in universe if mask // 2**a % 2} for mask in range(2**n)]
    mask = lambda s: sum(2**a for a in s)
    incoming = {a: {b for b, t in edges if t == a} for a in universe}
    rows = []
    for s in sets:
        attacked = {b for a, b in edges if a in s}
        defended = {a for a in universe if incoming[a] <= attacked}
        conflicts = [[a, b] for a, b in edges if a in s and b in s]
        defense = []
        for a in sorted(universe):
            responses = [
                {
                    "attacker": b,
                    "defenders": sorted(d for d, t in edges if t == b and d in s),
                }
                for b in sorted(incoming[a])
            ]
            unanswered = [r["attacker"] for r in responses if len(r["defenders"]) == 0]
            defense.append(
                {
                    "argument": a,
                    "responses": responses,
                    "unanswered": unanswered,
                    "defended": len(unanswered) == 0,
                }
            )
        rows.append(
            {
                "mask": mask(s),
                "attacked_mask": mask(attacked),
                "range_mask": mask(s | attacked),
                "defended_mask": mask(defended),
                "conflict_free": len(conflicts) == 0,
                "admissible": len(conflicts) == 0 and s <= defended,
                "complete": len(conflicts) == 0 and s == defended,
                "members": sorted(s),
                "conflicts": conflicts,
                "defense": defense,
            }
        )
    legal = []
    for labels in product(["in", "out", "undec"], repeat=n):
        if all(
            labels[a]
            == (
                "out"
                if any(labels[b] == "in" for b in incoming[a])
                else "in" if all(labels[b] == "out" for b in incoming[a]) else "undec"
            )
            for a in universe
        ):
            legal.append(
                (
                    {a for a in universe if labels[a] == "in"},
                    {a for a in universe if labels[a] == "undec"},
                )
            )
    complete = sorted(mask(s) for s, u in legal)
    preferred = sorted(mask(s) for s, u in legal if not any(s < t for t, _ in legal))
    semi = sorted(mask(s) for s, u in legal if not any(v < u for _, v in legal))
    grounded = sorted(mask(s) for s, u in legal if not any(t < s for t, _ in legal))
    assert len(grounded) == 1
    families = {
        "complete": complete,
        "preferred": preferred,
        "semi_stable": semi,
        "grounded": grounded,
    }
    cores = []
    for name, parent in [("ideal", "preferred"), ("eager", "semi_stable")]:
        parent_masks = families[parent]
        pool = set.intersection(*(sets[x] for x in parent_masks))
        admissible = [s for s, r in zip(sets, rows) if r["admissible"] and s <= pool]
        maximal = [s for s in admissible if not any(s < t for t in admissible)]
        by_complete = [
            s
            for s, u in legal
            if s <= pool and not any(s < t <= pool for t, v in legal)
        ]
        assert len(by_complete) == len(maximal) == 1 and by_complete == maximal
        answer = by_complete[0]
        total = set().union(*admissible)
        assert answer == total
        trace = []
        candidate = set(pool)
        while True:
            checks = [rows[mask(candidate)]["defense"][a] for a in sorted(candidate)]
            remove = {row["argument"] for row in checks if row["unanswered"]}
            remaining = candidate - remove
            trace.append(
                {
                    "round": len(trace),
                    "mask": mask(candidate),
                    "next_mask": mask(remaining),
                    "removed_mask": mask(remove),
                    "fixed": not remove,
                    "checks": checks,
                }
            )
            if not remove:
                break
            candidate = remaining
        assert candidate == answer
        induced = {(a, b) for a, b in edges if a in pool and b in pool}
        g = set()
        while True:
            defeated = {b for a, b in induced if a in g}
            nxt = {a for a in pool if {b for b, t in induced if t == a} <= defeated}
            if nxt == g:
                break
            g = nxt
        candidates = [
            {
                "mask": mask(s),
                "inside_pool": s <= pool,
                "eligible": s in admissible,
                "strict_eligible_supersets": sorted(
                    mask(t) for t in admissible if s < t
                ),
                "subset_of_result": s <= answer,
            }
            for s in sets
        ]
        acceptance = []
        for a in sorted(universe):
            removal = [r for r in trace if a in sets[r["removed_mask"]]]
            acceptance.append(
                {
                    "argument": a,
                    "containing_parent_extensions": [
                        s for s in parent_masks if a in sets[s]
                    ],
                    "excluding_parent_extensions": [
                        s for s in parent_masks if a not in sets[s]
                    ],
                    "in_pool": a in pool,
                    "in_core": a in answer,
                    "removed_round": removal[0]["round"] if removal else None,
                    "unanswered_when_removed": (
                        rows[removal[0]["mask"]]["defense"][a]["unanswered"]
                        if removal
                        else []
                    ),
                }
            )
        cores.append(
            {
                "semantics": name,
                "parent_semantics": parent,
                "parent_extensions": parent_masks,
                "pool_mask": mask(pool),
                "pool_admissible": rows[mask(pool)]["admissible"],
                "admissible_subsets": sorted(mask(s) for s in admissible),
                "maximal_admissible_subsets": sorted(mask(s) for s in maximal),
                "union_admissible_subsets": mask(total),
                "extension_mask": mask(answer),
                "pruning_trace": trace,
                "single_pass_mask": trace[0]["next_mask"],
                "induced_pool_grounded_mask": mask(g),
                "candidates": candidates,
                "acceptance": acceptance,
            }
        )
        families[name] = [mask(answer)]
    grounded = sets[families["grounded"][0]]
    ideal = sets[families["ideal"][0]]
    eager = sets[families["eager"][0]]
    return {
        "schema": "argumentlab-ideal-v1",
        "framework": framework,
        "subsets": rows,
        "families": families,
        "cores": cores,
        "inclusions": {
            "grounded_subset_ideal": grounded <= ideal,
            "ideal_subset_eager": ideal <= eager,
            "eager_subset_semistable_intersection": eager
            <= sets[cores[1]["pool_mask"]],
        },
        "limits": LIMITS[:],
    }


def exact(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def verify_ideal(report):
    if type(report) is not dict or "framework" not in report:
        raise ValueError("missing ideal/eager report framework")
    if not exact(report, expected(report["framework"])):
        raise ValueError(
            "ideal/eager evidence differs from independent set/labelling reconstruction"
        )
    return True
