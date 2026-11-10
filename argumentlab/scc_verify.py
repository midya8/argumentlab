"""Set/reachability and published fixed-point characterization verifier.
Shares input validation only, never calls the recursive generator.
"""
import json
from .core import validate


def verify_scc(report):
    if type(report) is not dict or 'framework' not in report:
        raise ValueError('expected SCC evidence')
    framework = validate(report['framework'])
    n = framework['arguments']
    if n > 6:
        raise ValueError('SCC inspector permits at most six arguments')
    vertices = set(range(n))
    edges = {tuple(e) for e in framework['attacks']}
    values = [{a for a in vertices if s >> a & 1} for s in range(1 << n)]
    mask = lambda value: sum(1 << a for a in value)
    solved = {}

    def graph(active):
        relation = {(a, b) for a, b in edges if a in active and b in active}
        reach = {}
        for a in sorted(active):
            visited, pending = {a}, [a]
            while pending:
                source = pending.pop()
                for x, y in sorted(relation):
                    if x == source and y not in visited:
                        visited.add(y)
                        pending.append(y)
            reach[a] = visited
        groups = []
        remaining = set(active)
        while remaining:
            a = min(remaining)
            component = {b for b in active if b in reach[a] and a in reach[b]}
            groups.append(component)
            remaining -= component
        return relation, reach, groups

    def census(active, relation):
        records = []
        for s in values:
            if not s <= active:
                continue
            conflicts = [[a, b] for a, b in sorted(relation) if {a, b} <= s]
            r = s | {b for a, b in relation if a in s}
            records.append((s, r, conflicts))
        return records

    def alternate(active, selected, semantics):
        relation, _, _ = graph(active)
        all_rows = census(active, relation)
        if any(conflicts for s, _, conflicts in all_rows if s == selected):
            return False
        if any(selected < s and not conflicts for s, _, conflicts in all_rows):
            return False
        defeated = set()
        while True:
            _, reach, _ = graph(active - defeated)
            new = {a for b, a in relation if b in selected and b != a and
                   (a not in reach or b not in reach[a])}
            if new == defeated:
                break
            if not defeated <= new:
                raise ValueError('component-defeat fixed point is not monotone')
            defeated = new
        remaining = active - defeated
        restricted, _, sccs = graph(remaining)
        separated = {(a, b) for a, b in restricted if any({a, b} <= c for c in sccs)}
        rows = census(remaining, separated)
        if not selected <= remaining:
            return False
        if semantics == 'cf2':
            return not any(selected < s and not conflicts for s, _, conflicts in rows)
        selected_range = selected | {b for a, b in separated if a in selected}
        return not any(selected_range < r and not conflicts for _, r, conflicts in rows)

    def reconstruct(active):
        key = mask(active)
        if key in solved:
            return solved[key]
        relation, reach, groups = graph(active)
        raw = census(active, relation)
        candidates = []
        cf = [(s, r) for s, r, conflicts in raw if not conflicts]
        for selected, ranged, conflicts in raw:
            larger = [mask(s) for s, _ in cf if selected < s]
            dominators = [mask(s) for s, r in cf if ranged < r]
            naive = not conflicts and not larger
            stage = not conflicts and not dominators
            defeating = [[a, b] for a, b in sorted(relation) if a in selected and
                         not any({a, b} <= c for c in groups)]
            removed = {b for _, b in defeating}
            obligations = []
            if len(groups) > 1:
                for component in groups:
                    surviving = component - removed
                    chosen = selected & component
                    child = reconstruct(surviving)
                    obligations.append({'component_mask': mask(component),
                                        'external_defeat_edges': [[a, b] for a, b in defeating if b in component],
                                        'defeated_mask': mask(component & removed),
                                        'surviving_mask': mask(surviving), 'selected_mask': mask(chosen),
                                        'selected_removed_mask': mask(chosen - surviving),
                                        'child_active_mask': mask(surviving),
                                        'child_cf2': mask(chosen) in child['cf2'],
                                        'child_stage2': mask(chosen) in child['stage2']})
            cf2 = naive if len(groups) <= 1 else all(o['child_cf2'] for o in obligations)
            stage2 = stage if len(groups) <= 1 else all(o['child_stage2'] for o in obligations)
            if cf2 != alternate(active, selected, 'cf2') or stage2 != alternate(active, selected, 'stage2'):
                raise ValueError('recursive evidence disagrees with fixed-point characterization')
            candidates.append({'mask': mask(selected), 'conflicts': conflicts,
                               'conflict_free': not conflicts, 'range_mask': mask(ranged),
                               'larger_conflict_free': larger, 'range_dominators': dominators,
                               'naive': naive, 'stage': stage,
                               'component_defeat_edges': defeating, 'component_defeated_mask': mask(removed),
                               'obligations': obligations, 'cf2': cf2, 'stage2': stage2})
        node = {'active_mask': key, 'attacks': [list(e) for e in sorted(relation)],
                'scc_masks': [mask(c) for c in groups],
                'reachability': [{'argument': a, 'reachable_mask': mask(reach[a])} for a in sorted(active)],
                'base_case': len(groups) <= 1, 'candidates': candidates,
                'naive': [r['mask'] for r in candidates if r['naive']],
                'stage': [r['mask'] for r in candidates if r['stage']],
                'cf2': [r['mask'] for r in candidates if r['cf2']],
                'stage2': [r['mask'] for r in candidates if r['stage2']]}
        solved[key] = node
        return node

    root = reconstruct(vertices)
    comparisons = []
    for name in ['naive', 'stage', 'cf2', 'stage2']:
        family = root[name]
        comparisons.append({'semantics': name, 'extensions': family,
                            'acceptance': [{'argument': a,
                                            'containing': [s for s in family if a in values[s]],
                                            'excluding': [s for s in family if a not in values[s]],
                                            'credulous': any(a in values[s] for s in family),
                                            'skeptical': all(a in values[s] for s in family)} for a in range(n)]})
    expected = {'schema': 'argumentlab-scc-v1', 'framework': framework,
                'root_active_mask': mask(vertices), 'subproblems': [solved[k] for k in sorted(solved)],
                'comparisons': comparisons,
                'cf2_not_stage2': sorted(set(root['cf2']) - set(root['stage2'])),
                'naive_not_cf2': sorted(set(root['naive']) - set(root['cf2'])),
                'stage_not_stage2': sorted(set(root['stage']) - set(root['stage2'])),
                'stage2_not_stage': sorted(set(root['stage2']) - set(root['stage']))}
    typed = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if typed(expected) != typed(report):
        raise ValueError('SCC evidence differs from independent reconstruction')
    return True
