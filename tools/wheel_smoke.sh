#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
uv build --wheel --out-dir "$tmp/dist" "$root"
uv venv "$tmp/env"
uv pip install --python "$tmp/env/bin/python" "$tmp"/dist/*.whl
cd "$tmp"
unset PYTHONPATH
"$tmp/env/bin/python" "$root/tools/verify_installed.py" "$root/docs/audits.json" "$root"
"$tmp/env/bin/argumentlab" "$root/examples/demo.json" --output "$tmp/console.json"
"$tmp/env/bin/python" -m argumentlab "$root/examples/demo.json" --output "$tmp/module.json"
cmp "$tmp/console.json" "$tmp/module.json"
printf '%s\n' 'Installed console/module CLI and all 19 reports/five module origins passed'
"$tmp/env/bin/argumentlab-switches" "$root/examples/switches.json" --configuration-mask 3 --output "$tmp/switch-console.json"
"$tmp/env/bin/python" -m argumentlab.switches "$root/examples/switches.json" --configuration-mask 3 --output "$tmp/switch-module.json"
cmp "$tmp/switch-console.json" "$tmp/switch-module.json"
printf '%s\n' 'Installed attack-switch console/module CLI,21 reports and209 configurations passed'
