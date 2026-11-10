"""Optional independent ASPARTIX comparison, no copied reference code vendored.
Fetch the two exact operator-hosted files named in SCC.md into --encoding-dir.
Run with clingo installed separately. Published bytes are pinned before use.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import clingo
from argumentlab.scc import audit_scc

PINNED = {
    'cf2': ('cf2.dl', 'ac02cb1bc64a86400982b09b49c5a8d9cdc774b6402fb17f632be29a2c0404d9'),
    'stage2': ('stage2_gringo.lp', '4c61429ba3d86f8a8ac0cbab4a7c0c64ec27c743c816744820373bc887526d00'),
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--encoding-dir', type=Path, required=True)
args = parser.parse_args()
encodings = {}
for name, (filename, digest) in PINNED.items():
    data = (args.encoding_dir / filename).read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('external encoding hash mismatch: ' + filename)
    encodings[name] = data.decode()
requests = families = 0


def check(framework):
    global requests, families
    report = audit_scc(framework)
    root = next(n for n in report['subproblems'] if n['active_mask'] == report['root_active_mask'])
    facts = ''.join('arg(%d).' % a for a in range(framework['arguments']))
    facts += ''.join('att(%d,%d).' % tuple(edge) for edge in framework['attacks'])
    for name, encoding in encodings.items():
        control = clingo.Control(['0', '--warn=none'])
        control.add('base', [], encoding + '\n' + facts)
        control.ground([('base', [])])
        observed = set()
        def receive(model):
            observed.add(sum(1 << x.arguments[0].number for x in model.symbols(atoms=True)
                             if x.name == 'in' and len(x.arguments) == 1))
        result = control.solve(on_model=receive)
        assert result.satisfiable and not result.interrupted
        assert sorted(observed) == root[name], (framework, name, sorted(observed), root[name])
        families += 1
    requests += 1


for n in range(4):
    for bits in range(1 << (n * n)):
        check({'arguments': n, 'attacks': [[a, b] for a in range(n) for b in range(n) if bits >> (a * n + b) & 1]})
rng = random.Random(7252)
for _ in range(180):
    n = rng.randrange(4, 7)
    check({'arguments': n, 'attacks': [[a, b] for a in range(n) for b in range(n) if rng.randrange(4) == 0]})
for c in json.loads((Path(__file__).resolve().parents[1] / 'docs/scc-controls.json').read_text()):
    check(c['framework'])
print(json.dumps({'reference': 'published ASPARTIX cf2.dl and stage2_gringo.lp',
                  'clingo': clingo.__version__, 'requests': requests,
                  'extension_families': families, 'encoding_hashes': {k: v[1] for k, v in PINNED.items()}}))
