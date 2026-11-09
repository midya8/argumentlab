"""Exhaustive finite Dung argumentation with complete computational witnesses."""
from __future__ import annotations
import json

MAX_ARGUMENTS = 8


def integer(x, lo, hi):
    if type(x) is not int or not lo <= x <= hi:
        raise ValueError(f'expected integer in [{lo},{hi}]')
    return x


def validate(raw):
    if type(raw) is not dict or set(raw) != {'arguments', 'attacks'}:
        raise ValueError('expected exactly arguments and attacks')
    n = integer(raw['arguments'], 0, MAX_ARGUMENTS)
    edges = raw['attacks']
    if type(edges) is not list or len(edges) > n*n:
        raise ValueError('expected at most n*n attack pairs')
    result = []
    for e in edges:
        if type(e) is not list or len(e) != 2:
            raise ValueError('attack must be [source,target]')
        result.append([integer(x, 0, n-1) for x in e])
    if len({tuple(e) for e in result}) != len(result):
        raise ValueError('duplicate attack')
    return {'arguments': n, 'attacks': sorted(result)}


def parse(text):
    if len(text.encode('utf8')) > 65536:
        raise ValueError('input exceeds 65536 UTF-8 bytes')
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate JSON key')
            d[k] = v
        return d
    return validate(json.loads(text, object_pairs_hook=pairs))


def audit(raw):
    p = validate(raw)
    n, edges = p['arguments'], p['attacks']
    full = (1 << n)-1
    members = lambda s: [a for a in range(n) if s & (1 << a)]
    incoming = [[b for b, target in edges if target == a] for a in range(n)]
    rows = []
    for s in range(1 << n):
        selected = members(s)
        attacked = sum(1 << a for a in range(n) if any(b in selected for b in incoming[a]))
        defense = []
        defended = 0
        for a in range(n):
            responses = [{'attacker': b, 'defenders': [c for c in selected if [c, b] in edges]} for b in incoming[a]]
            unanswered = [r['attacker'] for r in responses if not r['defenders']]
            if not unanswered:
                defended |= 1 << a
            defense.append({'argument': a, 'attackers': list(incoming[a]), 'responses': responses, 'unanswered': unanswered, 'defended': not unanswered})
        conflicts = [[a,b] for a,b in edges if a in selected and b in selected]
        cf = not conflicts
        adm = cf and s & defended == s
        rows.append({'mask': s, 'members': selected, 'attacked_mask': attacked, 'range_mask': s | attacked, 'defended_mask': defended, 'conflicts': conflicts, 'defense': defense, 'conflict_free': cf, 'admissible': adm, 'complete': adm and s == defended, 'stable': cf and (s | attacked) == full})
    strict_sub = lambda a,b: a != b and a & b == a
    cf_masks = [r['mask'] for r in rows if r['conflict_free']]
    adm_masks = [r['mask'] for r in rows if r['admissible']]
    complete = [r['mask'] for r in rows if r['complete']]
    for r in rows:
        s = r['mask']
        r['larger_conflict_free'] = [t for t in cf_masks if strict_sub(s,t)]
        r['larger_admissible'] = [t for t in adm_masks if strict_sub(s,t)]
        r['cf_range_dominators'] = [t for t in cf_masks if strict_sub(r['range_mask'],rows[t]['range_mask'])]
        r['admissible_range_dominators'] = [t for t in adm_masks if strict_sub(r['range_mask'],rows[t]['range_mask'])]
        r['naive'] = r['conflict_free'] and not r['larger_conflict_free']
        r['preferred'] = r['admissible'] and not r['larger_admissible']
        r['semi_stable'] = r['admissible'] and not r['admissible_range_dominators']
        r['stage'] = r['conflict_free'] and not r['cf_range_dominators']
    grounded_trace = []
    s = 0
    while True:
        nxt = rows[s]['defended_mask']
        grounded_trace.append({'step': len(grounded_trace), 'mask': s, 'next_mask': nxt, 'added_mask': nxt & ~s, 'fixed': nxt == s, 'defense': rows[s]['defense']})
        assert s & nxt == s
        if nxt == s:
            break
        s = nxt
    grounded = s
    families = {'conflict_free': cf_masks, 'admissible': adm_masks, 'complete': complete}
    for name in ['naive','preferred','stable','semi_stable','stage']:
        families[name] = [r['mask'] for r in rows if r[name]]
    families['grounded'] = [grounded]
    union_intersection = []
    for name, family in families.items():
        union, intersection = 0, full
        for t in family:
            union |= t
            intersection &= t
        acceptance = []
        for a in range(n):
            yes = [t for t in family if t & (1 << a)]
            no = [t for t in family if not t & (1 << a)]
            acceptance.append({'argument': a, 'credulous': bool(yes), 'skeptical_classical': not no, 'skeptical_nonvacuous': not no if family else None, 'containing_extensions': yes, 'excluding_extensions': no, 'witness_extension': yes[0] if yes else None, 'counterexample_extension': no[0] if no else None})
        union_intersection.append({'name': name, 'extensions': family, 'exists': bool(family), 'union_mask': union, 'intersection_classical_mask': intersection, 'intersection_nonvacuous_mask': intersection if family else None, 'acceptance': acceptance})
    labellings = []
    for t in complete:
        out = rows[t]['attacked_mask']
        labels = ['in' if t & (1 << a) else 'out' if out & (1 << a) else 'undec' for a in range(n)]
        legal = []
        for a in range(n):
            ins = [b for b in incoming[a] if labels[b] == 'in']
            undecs = [b for b in incoming[a] if labels[b] == 'undec']
            expected = 'out' if ins else 'undec' if undecs else 'in'
            assert labels[a] == expected
            legal.append({'argument': a, 'label': labels[a], 'attacker_labels': [[b,labels[b]] for b in incoming[a]], 'in_attackers': ins, 'undec_attackers': undecs, 'legal': True})
        labellings.append({'extension_mask': t, 'in_mask': t, 'out_mask': out, 'undec_mask': full & ~(t | out), 'labels': labels, 'legality': legal})
    assert grounded in complete
    assert all(grounded & t == grounded for t in complete)
    assert set(families['stable']) <= set(families['semi_stable']) <= set(families['preferred']) <= set(complete) <= set(adm_masks) <= set(cf_masks)
    assert set(families['stable']) <= set(families['stage']) <= set(families['naive']) <= set(cf_masks)
    preferred_intersection = full
    for t in families['preferred']:
        preferred_intersection &= t
    maximum_admissible_size = max(t.bit_count() for t in adm_masks)
    return {'schema':'argumentlab/1', 'input':p, 'incoming': incoming, 'subsets':rows, 'families':union_intersection, 'grounded_trace':grounded_trace, 'complete_labellings':labellings, 'contrasts':{'grounded_mask':grounded, 'preferred_intersection_mask':preferred_intersection, 'preferred_intersection_is_admissible':rows[preferred_intersection]['admissible'], 'preferred_not_maximum_cardinality':[t for t in families['preferred'] if t.bit_count() < maximum_admissible_size], 'maximum_cardinality_admissible':[t for t in adm_masks if t.bit_count() == maximum_admissible_size]}, 'checks':{'subsets':len(rows),'complete_labellings':len(labellings),'grounded_fixed_point':True,'grounded_least_complete':True,'family_inclusions':True,'complete_labelling_legality':True}}
