"""Run from outside the checkout with an installed wheel."""
import importlib
import json
import pathlib
import sys
from argumentlab import audit
fixture=pathlib.Path(sys.argv[1]);source=pathlib.Path(sys.argv[2]).resolve()
origins={}
for name in ['argumentlab','argumentlab.core','argumentlab.cli','argumentlab.__main__','argumentlab.switches','argumentlab.scc','argumentlab.scc_verify','argumentlab.ideal','argumentlab.ideal_input','argumentlab.ideal_verify','argumentlab.ideal_cli']:
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

from argumentlab.scc import audit_scc
from argumentlab.scc_verify import verify_scc
controls=json.loads((fixture.parent/'scc-controls.json').read_text())
for row in controls:
    report=audit_scc(row['framework'])
    assert verify_scc(report)
    forged=json.loads(json.dumps(report));forged['root_active_mask']=True
    try: verify_scc(forged)
    except (ValueError,TypeError): pass
    else: raise AssertionError('forged root accepted')
print(json.dumps({'installed_scc_reports':len(controls),'rejected_forgeries':len(controls)}))

from argumentlab.ideal import audit_ideal
from argumentlab.ideal_verify import verify_ideal
controls=json.loads((fixture.parent/'ideal-controls.json').read_text())
for row in controls:
    r=audit_ideal(row['framework']);assert verify_ideal(r)
    forged=json.loads(json.dumps(r));forged['cores'][0]['extension_mask']=True
    try:verify_ideal(forged)
    except (ValueError,TypeError):pass
    else:raise AssertionError('forged core accepted')
print(json.dumps({'installed_ideal_reports':len(controls),'rejected_forgeries':len(controls)}))
