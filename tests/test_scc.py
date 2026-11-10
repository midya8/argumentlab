import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from argumentlab.core import audit
from argumentlab.scc import audit_scc
from argumentlab.scc_verify import verify_scc

ROOT = Path(__file__).resolve().parents[1]
CONTROLS = json.loads((ROOT / 'docs/scc-controls.json').read_text())


class SCCTests(unittest.TestCase):
    def test_all_531_small_frameworks(self):
        count = 0
        for n in range(4):
            for bits in range(1 << (n * n)):
                data = {'arguments': n, 'attacks': [[a, b] for a in range(n) for b in range(n) if bits >> (a * n + b) & 1]}
                report = audit_scc(data)
                self.assertTrue(verify_scc(report))
                root = next(x for x in report['subproblems'] if x['active_mask'] == report['root_active_mask'])
                old = {x['name']: x['extensions'] for x in audit(data)['families']}
                self.assertEqual(root['naive'], old['naive'])
                self.assertEqual(root['stage'], old['stage'])
                self.assertTrue(set(root['stage2']) <= set(root['cf2']) <= set(root['naive']))
                self.assertTrue(set(old['stable']) <= set(root['stage2']))
                self.assertTrue(root['cf2'] and root['stage2'])
                count += 1
        self.assertEqual(count, 531)

    def test_seeded_larger_and_no_mutation(self):
        rng = random.Random(7252)
        for _ in range(180):
            n = rng.randrange(4, 7)
            data = {'arguments': n, 'attacks': [[a, b] for a in range(n) for b in range(n) if rng.randrange(4) == 0]}
            rng.shuffle(data['attacks'])
            before = copy.deepcopy(data)
            report = audit_scc(data)
            self.assertTrue(verify_scc(report))
            self.assertEqual(data, before)
            self.assertEqual(report['framework']['attacks'], sorted(before['attacks']))

    def test_strict_controls_and_recursive_split(self):
        for c in CONTROLS:
            self.assertTrue(verify_scc(audit_scc(c['framework'])))
        source = audit_scc(CONTROLS[2]['framework'])
        self.assertEqual(source['naive_not_cf2'], [2])
        six = audit_scc(CONTROLS[5]['framework'])
        self.assertEqual(six['cf2_not_stage2'], [9, 18, 36])
        self.assertEqual(audit_scc(CONTROLS[9]['framework'])['stage2_not_stage'], [10])
        cascade = audit_scc(CONTROLS[7]['framework'])
        root = next(n for n in cascade['subproblems'] if n['active_mask'] == 31)
        selected = next(r for r in root['candidates'] if r['mask'] == 21)
        child = next(o for o in selected['obligations'] if o['component_mask'] == 30)
        self.assertEqual(child['surviving_mask'], 28)
        sub = next(n for n in cascade['subproblems'] if n['active_mask'] == 28)
        self.assertEqual(sub['scc_masks'], [4, 8, 16])
        row = next(r for r in sub['candidates'] if r['mask'] == 20)
        self.assertEqual(row['component_defeated_mask'], 8)
        self.assertTrue(row['cf2'] and row['stage2'])
        empty = audit_scc(CONTROLS[0]['framework'])
        self.assertEqual(empty['subproblems'][0]['cf2'], [0])

    def test_permutations(self):
        for c in CONTROLS:
            n = c['framework']['arguments']
            if not n:
                continue
            permutation = list(reversed(range(n)))
            data = {'arguments': n, 'attacks': [[permutation[a], permutation[b]] for a, b in c['framework']['attacks']]}
            old, new = audit_scc(c['framework']), audit_scc(data)
            translate = lambda s: sum(1 << permutation[a] for a in range(n) if s >> a & 1)
            for left, right in zip(old['comparisons'], new['comparisons']):
                self.assertEqual(sorted(map(translate, left['extensions'])), right['extensions'])
            self.assertTrue(verify_scc(new))

    def test_scalar_forgery_and_missing_records(self):
        def leaves(x, path=()):
            if type(x) is dict:
                for k, v in x.items():
                    if not path and k == 'framework':
                        continue
                    yield from leaves(v, path + (k,))
            elif type(x) is list:
                for i, v in enumerate(x):
                    yield from leaves(v, path + (i,))
            else:
                yield path, x
        count = 0
        for c in [CONTROLS[2], CONTROLS[3]]:
            report = audit_scc(c['framework'])
            for path, value in leaves(report):
                forged = copy.deepcopy(report)
                parent = forged
                for k in path[:-1]:
                    parent = parent[k]
                parent[path[-1]] = not value if type(value) is bool else value + 1 if type(value) is int else 'forged'
                with self.assertRaises(ValueError, msg=str(path)):
                    verify_scc(forged)
                count += 1
            for key in report:
                forged = copy.deepcopy(report)
                del forged[key]
                with self.assertRaises(ValueError):
                    verify_scc(forged)
            forged = copy.deepcopy(report)
            forged['subproblems'].pop()
            with self.assertRaises(ValueError):
                verify_scc(forged)
            with self.assertRaises(ValueError):
                verify_scc({**report, 'extra': True})
        self.assertGreater(count, 200)

    def test_schema_and_verifier_isolation(self):
        for bad in [None, [], {}, {'arguments': True, 'attacks': []}, {'arguments': 7, 'attacks': []}, {'arguments': 2, 'attacks': [[0, 2]]}, {'arguments': 2, 'attacks': [[0, 1], [0, 1]]}, {'arguments': 2, 'attacks': [[False, 1]]}, {'arguments': 2, 'attacks': [[0]]}]:
            with self.assertRaises(ValueError):
                audit_scc(bad)
        report = audit_scc(CONTROLS[7]['framework'])
        with patch('argumentlab.scc.audit_scc', side_effect=AssertionError('generator called')):
            self.assertTrue(verify_scc(report))

    def test_cli_roundtrip_atomic_and_strict_json(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / 'out.json'
            run = lambda args, **kw: subprocess.run([sys.executable, '-m', 'argumentlab.scc', *args], capture_output=True, **kw)
            result = run([str(ROOT / 'examples/scc.json'), '-o', str(output)])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(run(['--verify', str(output)]).returncode, 0)
            report = json.loads(output.read_text())
            report['schema'] = 'forged'
            for verify, body in [(True, json.dumps(report).encode()), (False, b'{"arguments":0,"arguments":1,"attacks":[]}'), (False, b'NaN'), (False, b'\xff'), (False, b' ' * 65537)]:
                before = output.read_bytes()
                bad = run((['--verify'] if verify else []) + ['-', '-o', str(output)], input=body)
                self.assertEqual(bad.returncode, 2, bad.stderr)
                self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
