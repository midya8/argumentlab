"""Run from outside the checkout with an installed wheel."""
import importlib
import json
import pathlib
import sys
from argumentlab import audit
fixture=pathlib.Path(sys.argv[1]);source=pathlib.Path(sys.argv[2]).resolve()
origins={}
for name in ['argumentlab','argumentlab.core','argumentlab.cli','argumentlab.__main__','argumentlab.switches']:
    path=pathlib.Path(importlib.import_module(name).__file__).resolve()
    assert source not in path.parents,(name,path)
    assert 'site-packages' in str(path),(name,path)
    origins[name]=str(path)
rows=json.loads(fixture.read_text())
for row in rows:assert audit(row['input'])==row['report'],row['name']
print(json.dumps({'reports':len(rows),'module_origins':origins}))

from argumentlab.switches import sensitivity,framework_at
switch_rows=json.loads((fixture.parent/'switch-audits.json').read_text())
for row in switch_rows:
    assert sensitivity(row['input'])==row['report'],row['name']
    for c in row['report']['configurations']:assert framework_at(row['input'],c['mask'])==c['framework']
print(json.dumps({'installed_switch_reports':len(switch_rows),'switch_configurations':sum(len(r['report']['configurations']) for r in switch_rows)}))
