"""Bounded SCC-recursive CF2/stage2 definition with complete subproblem evidence."""
from .core import validate


def audit_scc(raw):
    request = validate(raw)
    n, attacks = request['arguments'], request['attacks']
    if n > 6:
        raise ValueError('SCC inspector permits at most six arguments')
    full = (1 << n) - 1
    nodes = {}

    def components(active):
        reach = {a: 1 << a for a in range(n) if active >> a & 1}
        for a, b in attacks:
            if a in reach and b in reach:
                reach[a] |= 1 << b
        for k in reach:
            for a in reach:
                if reach[a] >> k & 1:
                    reach[a] |= reach[k]
        remaining, result = active, []
        while remaining:
            a = (remaining & -remaining).bit_length() - 1
            c = sum(1 << b for b in reach if reach[a] >> b & 1 and reach[b] >> a & 1)
            result.append(c)
            remaining &= ~c
        return result, [{'argument': a, 'reachable_mask': reach[a]} for a in reach]

    def solve(active):
        if active in nodes:
            return nodes[active]
        sccs, reach = components(active)
        edges = [[a, b] for a, b in attacks if active >> a & 1 and active >> b & 1]
        masks = [s for s in range(full + 1) if s & active == s]
        rows = []
        for s in masks:
            conflicts = [[a, b] for a, b in edges if s >> a & 1 and s >> b & 1]
            attacked = sum(1 << b for b in range(n) if any(s >> a & 1 for a, t in edges if t == b))
            rows.append({'mask': s, 'conflicts': conflicts, 'conflict_free': not conflicts,
                         'range_mask': s | attacked})
        cf = [r for r in rows if r['conflict_free']]
        for row in rows:
            s = row['mask']
            row['larger_conflict_free'] = [r['mask'] for r in cf if r['mask'] != s and r['mask'] & s == s]
            row['range_dominators'] = [r['mask'] for r in cf if r['range_mask'] != row['range_mask'] and r['range_mask'] & row['range_mask'] == row['range_mask']]
            row['naive'] = row['conflict_free'] and not row['larger_conflict_free']
            row['stage'] = row['conflict_free'] and not row['range_dominators']
            component_of = {a: c for c in sccs for a in range(n) if c >> a & 1}
            defeating = [[a, b] for a, b in edges if s >> a & 1 and component_of[a] != component_of[b]]
            defeated = sum(1 << b for b in range(n) if any(t == b for _, t in defeating))
            obligations = []
            if len(sccs) > 1:
                for c in sccs:
                    surviving = c & ~defeated
                    chosen = s & c
                    child = solve(surviving)
                    obligations.append({'component_mask': c, 'external_defeat_edges': [[a, b] for a, b in defeating if c >> b & 1],
                                        'defeated_mask': c & defeated, 'surviving_mask': surviving,
                                        'selected_mask': chosen, 'selected_removed_mask': chosen & ~surviving,
                                        'child_active_mask': surviving,
                                        'child_cf2': chosen in child['cf2'],
                                        'child_stage2': chosen in child['stage2']})
            row.update({'component_defeat_edges': defeating, 'component_defeated_mask': defeated,
                        'obligations': obligations,
                        'cf2': row['naive'] if len(sccs) <= 1 else all(o['child_cf2'] for o in obligations),
                        'stage2': row['stage'] if len(sccs) <= 1 else all(o['child_stage2'] for o in obligations)})
        result = {'active_mask': active, 'attacks': edges, 'scc_masks': sccs,
                  'reachability': reach, 'base_case': len(sccs) <= 1,
                  'candidates': rows,
                  'naive': [r['mask'] for r in rows if r['naive']],
                  'stage': [r['mask'] for r in rows if r['stage']],
                  'cf2': [r['mask'] for r in rows if r['cf2']],
                  'stage2': [r['mask'] for r in rows if r['stage2']]}
        nodes[active] = result
        return result

    root = solve(full)
    comparisons = []
    for name in ['naive', 'stage', 'cf2', 'stage2']:
        family = root[name]
        comparisons.append({'semantics': name, 'extensions': family,
                            'acceptance': [{'argument': a,
                                            'containing': [s for s in family if s >> a & 1],
                                            'excluding': [s for s in family if not s >> a & 1],
                                            'credulous': any(s >> a & 1 for s in family),
                                            'skeptical': all(s >> a & 1 for s in family)} for a in range(n)]})
    return {'schema': 'argumentlab-scc-v1', 'framework': request,
            'root_active_mask': full, 'subproblems': [nodes[a] for a in sorted(nodes)],
            'comparisons': comparisons,
            'cf2_not_stage2': sorted(set(root['cf2']) - set(root['stage2'])),
            'naive_not_cf2': sorted(set(root['naive']) - set(root['cf2'])),
            'stage_not_stage2': sorted(set(root['stage']) - set(root['stage2'])),
            'stage2_not_stage': sorted(set(root['stage2']) - set(root['stage']))}


def main(argv=None):
    """Strict JSON SCC generation/checking with atomic output replacement."""
    import argparse
    import json
    import os
    from pathlib import Path
    import sys
    import tempfile
    from .scc_verify import verify_scc
    parser = argparse.ArgumentParser(description='Exact finite SCC-recursive argumentation evidence')
    parser.add_argument('input', help='UTF-8 JSON path or - for stdin')
    parser.add_argument('--verify', action='store_true', help='independently check an exported SCC report')
    parser.add_argument('-o', '--output')
    args = parser.parse_args(argv)
    limit = 4 * 1024 * 1024 if args.verify else 65536
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    try:
        raw = sys.stdin.buffer.read(limit + 1) if args.input == '-' else Path(args.input).read_bytes()
        if len(raw) > limit:
            raise ValueError('input exceeds mode UTF-8 byte limit')
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON constant')))
        if args.verify:
            verify_scc(data)
            result = {'valid': True, 'schema': 'argumentlab-scc-v1'}
        else:
            result = audit_scc(data)
        text = json.dumps(result, indent=2, allow_nan=False) + '\n'
        if args.output:
            target = Path(args.output)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=target.parent, delete=False) as f:
                temporary = f.name
                try:
                    f.write(text)
                except BaseException:
                    os.unlink(temporary)
                    raise
            try:
                os.replace(temporary, target)
            except BaseException:
                os.unlink(temporary)
                raise
        else:
            sys.stdout.write(text)
    except (ValueError, OSError, UnicodeError, RecursionError) as error:
        parser.exit(2, 'Invalid input: ' + str(error) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
