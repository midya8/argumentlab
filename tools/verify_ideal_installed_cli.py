"""Check every installed CLI control and selected forged reports outside checkout."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from argumentlab.ideal import audit_ideal

root, console, python = sys.argv[1:]
controls = json.loads((Path(root) / "docs/ideal-controls.json").read_text())
with tempfile.TemporaryDirectory() as temp:
    out = Path(temp) / "report.json"
    verified = 0
    for row in controls:
        framework = json.dumps(row["framework"])
        a = subprocess.run(
            [console, "-"], input=framework, text=True, capture_output=True, check=True
        )
        b = subprocess.run(
            [python, "-m", "argumentlab.ideal_cli", "-"],
            input=framework,
            text=True,
            capture_output=True,
            check=True,
        )
        assert a.stdout == b.stdout
        report = json.loads(a.stdout)
        assert report == audit_ideal(row["framework"])
        for cmd in [[console], [python, "-m", "argumentlab.ideal_cli"]]:
            checked = subprocess.run(
                cmd + ["-", "--verify"],
                input=a.stdout,
                text=True,
                capture_output=True,
                check=True,
            )
            assert json.loads(checked.stdout)["valid"] is True
        verified += 1
    report = audit_ideal(controls[0]["framework"])
    mutations = [
        ("cores", 0, "extension_mask"),
        ("cores", 0, "pool_mask"),
        ("cores", 0, "single_pass_mask"),
        ("cores", 1, "extension_mask"),
        ("cores", 0, "pruning_trace", 1, "removed_mask"),
        ("cores", 0, "pruning_trace", 0, "checks", 0, "defended"),
        ("cores", 0, "candidates", 0, "eligible"),
        ("cores", 0, "acceptance", 3, "removed_round"),
        ("families", "preferred", 0),
        ("subsets", 0, "admissible"),
    ]
    rejected = 0
    for trail in mutations:
        forged = copy.deepcopy(report)
        dst = forged
        for k in trail[:-1]:
            dst = dst[k]
        v = dst[trail[-1]]
        dst[trail[-1]] = not v if type(v) is bool else v + 1
        for cmd in [[console], [python, "-m", "argumentlab.ideal_cli"]]:
            out.write_text("preserve")
            r = subprocess.run(
                cmd + ["-", "--verify", "--output", str(out)],
                input=json.dumps(forged),
                text=True,
                capture_output=True,
            )
            assert r.returncode == 2 and out.read_text() == "preserve"
            assert "Traceback" not in r.stderr
            rejected += 1
    print(
        json.dumps(
            {
                "installed_ideal_controls": verified,
                "entrypoints": 2,
                "forged_cli_rejections": rejected,
                "atomic_preservation_checks": rejected,
            }
        )
    )
