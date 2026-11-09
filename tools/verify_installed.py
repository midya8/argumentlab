"""Run from outside the checkout with an installed wheel."""
import importlib
import json
import pathlib
import sys
from argumentlab import audit
fixture=pathlib.Path(sys.argv[1]);source=pathlib.Path(sys.argv[2]).resolve()
origins={}
for name in ['argumentlab','argumentlab.core','argumentlab.cli','argumentlab.__main__']:
    path=pathlib.Path(importlib.import_module(name).__file__).resolve()
    assert source not in path.parents,(name,path)
    assert 'site-packages' in str(path),(name,path)
    origins[name]=str(path)
rows=json.loads(fixture.read_text())
for row in rows:assert audit(row['input'])==row['report'],row['name']
print(json.dumps({'reports':len(rows),'module_origins':origins}))
