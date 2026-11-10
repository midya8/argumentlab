"""Exact finite ideal/eager cores with original-graph defense pruning."""

from .ideal_input import validate, LIMITS


def summary(n, edges):
    incoming = [sum(1 << a for a, b in edges if b == v) for v in range(n)]
    outgoing = [sum(1 << b for a, b in edges if a == v) for v in range(n)]
    rows = []
    for mask in range(1 << n):
        attacked = 0
        for a in range(n):
            if mask >> a & 1:
                attacked |= outgoing[a]
        defended = sum(
            1 << a for a in range(n) if incoming[a] & attacked == incoming[a]
        )
        cf = not (mask & attacked)
        adm = cf and mask & defended == mask
        rows.append(
            {
                "mask": mask,
                "attacked_mask": attacked,
                "range_mask": mask | attacked,
                "defended_mask": defended,
                "conflict_free": cf,
                "admissible": adm,
                "complete": adm and mask == defended,
            }
        )
    adm = [r["mask"] for r in rows if r["admissible"]]
    complete = [r["mask"] for r in rows if r["complete"]]
    preferred = [s for s in adm if not any(s != t and s & t == s for t in adm)]
    semi = [
        s
        for s in adm
        if not any(
            rows[s]["range_mask"] != rows[t]["range_mask"]
            and rows[s]["range_mask"] & rows[t]["range_mask"] == rows[s]["range_mask"]
            for t in adm
        )
    ]
    g = 0
    while rows[g]["defended_mask"] != g:
        g = rows[g]["defended_mask"]
    return (
        rows,
        {
            "complete": complete,
            "preferred": preferred,
            "semi_stable": semi,
            "grounded": [g],
        },
        incoming,
    )


def audit_ideal(raw):
    framework = validate(raw)
    n = framework["arguments"]
    edges = framework["attacks"]
    full = (1 << n) - 1
    rows, families, incoming = summary(n, edges)
    members = lambda s: [a for a in range(n) if s >> a & 1]
    for row in rows:
        s = row["mask"]
        row["members"] = members(s)
        row["conflicts"] = [[a, b] for a, b in edges if s >> a & 1 and s >> b & 1]
        row["defense"] = []
        for a in range(n):
            replies = [
                {"attacker": b, "defenders": [d for d in members(s) if [d, b] in edges]}
                for b in members(incoming[a])
            ]
            unanswered = [r["attacker"] for r in replies if not r["defenders"]]
            row["defense"].append(
                {
                    "argument": a,
                    "responses": replies,
                    "unanswered": unanswered,
                    "defended": not unanswered,
                }
            )
    cores = []
    for name, parent in [("ideal", "preferred"), ("eager", "semi_stable")]:
        family = families[parent]
        pool = full
        for mask in family:
            pool &= mask
        eligible = [
            r["mask"] for r in rows if r["admissible"] and r["mask"] & pool == r["mask"]
        ]
        maximal = [
            s for s in eligible if not any(s != t and s & t == s for t in eligible)
        ]
        union = 0
        for s in eligible:
            union |= s
        assert maximal == [union] and rows[union]["complete"]
        trace = []
        current = pool
        while True:
            nxt = current & rows[current]["defended_mask"]
            trace.append(
                {
                    "round": len(trace),
                    "mask": current,
                    "next_mask": nxt,
                    "removed_mask": current & ~nxt,
                    "fixed": current == nxt,
                    "checks": [rows[current]["defense"][a] for a in members(current)],
                }
            )
            if current == nxt:
                break
            current = nxt
        assert current == union
        induced = [[a, b] for a, b in edges if pool >> a & 1 and pool >> b & 1]
        active = 0
        while True:
            attacked = sum(
                1 << a
                for a in range(n)
                if any(active >> b & 1 for b, t in induced if t == a)
            )
            nxt = sum(
                1 << a
                for a in members(pool)
                if all(attacked >> b & 1 for b, t in induced if t == a)
            )
            if active == nxt:
                break
            active = nxt
        candidates = [
            {
                "mask": r["mask"],
                "inside_pool": r["mask"] & pool == r["mask"],
                "eligible": r["mask"] in eligible,
                "strict_eligible_supersets": [
                    t for t in eligible if t != r["mask"] and t & r["mask"] == r["mask"]
                ],
                "subset_of_result": r["mask"] & union == r["mask"],
            }
            for r in rows
        ]
        acceptance = []
        for a in range(n):
            removed = next((t for t in trace if t["removed_mask"] >> a & 1), None)
            acceptance.append(
                {
                    "argument": a,
                    "containing_parent_extensions": [s for s in family if s >> a & 1],
                    "excluding_parent_extensions": [
                        s for s in family if not s >> a & 1
                    ],
                    "in_pool": bool(pool >> a & 1),
                    "in_core": bool(union >> a & 1),
                    "removed_round": None if removed is None else removed["round"],
                    "unanswered_when_removed": (
                        []
                        if removed is None
                        else rows[removed["mask"]]["defense"][a]["unanswered"]
                    ),
                }
            )
        cores.append(
            {
                "semantics": name,
                "parent_semantics": parent,
                "parent_extensions": family,
                "pool_mask": pool,
                "pool_admissible": rows[pool]["admissible"],
                "admissible_subsets": eligible,
                "maximal_admissible_subsets": maximal,
                "union_admissible_subsets": union,
                "extension_mask": union,
                "pruning_trace": trace,
                "single_pass_mask": trace[0]["next_mask"],
                "induced_pool_grounded_mask": active,
                "candidates": candidates,
                "acceptance": acceptance,
            }
        )
        families[name] = [union]
    g = families["grounded"][0]
    ideal = families["ideal"][0]
    eager = families["eager"][0]
    return {
        "schema": "argumentlab-ideal-v1",
        "framework": framework,
        "subsets": rows,
        "families": families,
        "cores": cores,
        "inclusions": {
            "grounded_subset_ideal": g & ideal == g,
            "ideal_subset_eager": ideal & eager == ideal,
            "eager_subset_semistable_intersection": eager & cores[1]["pool_mask"]
            == eager,
        },
        "limits": LIMITS[:],
    }
