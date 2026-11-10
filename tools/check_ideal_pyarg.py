"""Optional actual PyArg2.0.2 comparison. No external solver code is vendored.

pip install python-argumentation==2.0.2
PYTHONPATH=. python tools/check_ideal_pyarg.py
"""

import importlib.metadata, json
from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import (
    AbstractArgumentationFramework,
)
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.algorithms.semantics.get_ideal_extension import get_ideal_extension
from py_arg.algorithms.semantics.get_eager_extension import get_eager_extension
from argumentlab.ideal import audit_ideal
from tools.ideal_cases import controls, exhaustive, seeded

version = importlib.metadata.version("python-argumentation")
assert version == "2.0.2"
count = 0
for data in list(exhaustive()) + seeded() + [c["framework"] for c in controls()]:
    args = [Argument("a" + str(i)) for i in range(data["arguments"])]
    af = AbstractArgumentationFramework(
        "original-probe", args, [Defeat(args[a], args[b]) for a, b in data["attacks"]]
    )
    r = audit_ideal(data)
    for name, solver in [
        ("ideal", get_ideal_extension),
        ("eager", get_eager_extension),
    ]:
        actual = sorted(
            sum(1 << i for i, a in enumerate(args) if a in s) for s in solver(af)
        )
        assert actual == r["families"][name], (data, name, actual, r["families"][name])
    count += 1
print(
    json.dumps(
        {
            "reference": "python-argumentation",
            "version": version,
            "frameworks": count,
            "extension_families": 2 * count,
        }
    )
)
