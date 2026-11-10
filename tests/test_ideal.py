import copy, json, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
from argumentlab.ideal import audit_ideal
from argumentlab.ideal_verify import verify_ideal
from argumentlab.core import audit
from tools.ideal_cases import controls, exhaustive, seeded


class IdealTests(unittest.TestCase):
    def test_full_independent_reports(self):
        for data in (
            list(exhaustive()) + seeded() + [c["framework"] for c in controls()]
        ):
            self.assertTrue(verify_ideal(audit_ideal(data)))

    def test_original_family_agreement(self):
        for data in list(exhaustive()) + seeded(40):
            r = audit_ideal(data)
            base = {f["name"]: f["extensions"] for f in audit(data)["families"]}
            for k in ["complete", "preferred", "semi_stable", "grounded"]:
                self.assertEqual(r["families"][k], base[k])

    def test_cascade_not_one_pass(self):
        r = audit_ideal(controls()[0]["framework"])
        c = r["cores"][0]
        self.assertEqual(c["parent_extensions"], [156, 184])
        self.assertEqual(c["pool_mask"], 152)
        self.assertEqual([t["mask"] for t in c["pruning_trace"]], [152, 136, 128])
        self.assertEqual([t["removed_mask"] for t in c["pruning_trace"]], [16, 8, 0])
        self.assertEqual(c["extension_mask"], 128)
        self.assertEqual(c["single_pass_mask"], 136)

    def test_outside_attackers_not_deleted(self):
        r = audit_ideal(controls()[0]["framework"])
        c = r["cores"][0]
        self.assertEqual(c["induced_pool_grounded_mask"], 152)
        self.assertNotEqual(c["extension_mask"], c["induced_pool_grounded_mask"])
        self.assertIn(0, r["subsets"][c["pool_mask"]]["defense"][4]["unanswered"])
        self.assertIn(6, r["subsets"][136]["defense"][3]["unanswered"])

    def test_nonempty_core(self):
        c = audit_ideal(controls()[1]["framework"])["cores"][0]
        self.assertEqual(c["pool_mask"], 6)
        self.assertEqual(c["extension_mask"], 2)
        self.assertFalse(c["pool_admissible"])

    def test_grounded_strict_ideal(self):
        f = audit_ideal(controls()[2]["framework"])["families"]
        self.assertEqual(f["grounded"], [0])
        self.assertEqual(f["ideal"], [3])

    def test_ideal_strict_eager(self):
        f = audit_ideal(controls()[3]["framework"])["families"]
        self.assertEqual(f["ideal"], [0])
        self.assertEqual(f["eager"], [3])

    def test_empty_family_not_empty_extension(self):
        for i in [5, 7, 9, 11]:
            r = audit_ideal(controls()[i]["framework"])
            for k in ["preferred", "semi_stable", "ideal", "eager"]:
                self.assertEqual(r["families"][k], [0])

    def test_all_eligible_sets_in_unique_greatest_complete(self):
        for data in seeded():
            r = audit_ideal(data)
            self.assertTrue(all(r["inclusions"].values()))
            for c in r["cores"]:
                ans = c["extension_mask"]
                self.assertTrue(r["subsets"][ans]["complete"])
                self.assertEqual(c["maximal_admissible_subsets"], [ans])
                self.assertTrue(all(s & ans == s for s in c["admissible_subsets"]))

    def test_strict_malformed(self):
        for x in [
            None,
            [],
            {},
            {"arguments": True, "attacks": []},
            {"arguments": 9, "attacks": []},
            {"arguments": 1, "attacks": [[0, 0], [0, 0]]},
            {"arguments": 1, "attacks": [[True, 0]]},
            {"arguments": 1, "attacks": [[0, 1]]},
            {"arguments": 0, "attacks": [[0, 0]]},
            {"arguments": 1, "attacks": [[0]]},
        ]:
            with self.assertRaises(ValueError):
                audit_ideal(x)

    def test_permutation(self):
        d = controls()[0]["framework"]
        n = d["arguments"]
        perm = [5, 1, 6, 3, 7, 0, 2, 4]
        x = {"arguments": n, "attacks": [[perm[a], perm[b]] for a, b in d["attacks"]]}
        before = audit_ideal(d)
        after = audit_ideal(x)
        rename = lambda s: sum(1 << perm[a] for a in range(n) if s >> a & 1)
        for k, ss in before["families"].items():
            self.assertEqual(sorted(map(rename, ss)), after["families"][k])

    def test_checker_does_not_call_either_generator(self):
        r = audit_ideal(controls()[0]["framework"])
        with patch("argumentlab.ideal.audit_ideal", side_effect=AssertionError), patch(
            "argumentlab.ideal.summary", side_effect=AssertionError
        ), patch("argumentlab.core.audit", side_effect=AssertionError):
            self.assertTrue(verify_ideal(r))

    def test_small_control_every_noninput_leaf_tamper(self):
        report = audit_ideal(controls()[2]["framework"])
        count = 0

        def walk(x, path=()):
            if isinstance(x, dict):
                for k, v in x.items():
                    if path or k != "framework":
                        yield from walk(v, path + (k,))
            elif isinstance(x, list):
                for i, v in enumerate(x):
                    yield from walk(v, path + (i,))
            else:
                yield path, x

        for path, value in walk(report):
            x = copy.deepcopy(report)
            dst = x
            for k in path[:-1]:
                dst = dst[k]
            dst[path[-1]] = (
                not value
                if type(value) is bool
                else (
                    value + 1
                    if type(value) is int
                    else "corrupt" if type(value) is str else 0
                )
            )
            with self.assertRaises(ValueError):
                verify_ideal(x)
            count += 1
        for x in [
            dict(report, extra=0),
            {k: v for k, v in report.items() if k != "limits"},
            dict(report, inclusions=1),
        ]:
            with self.assertRaises(ValueError):
                verify_ideal(x)
        print("ideal/eager mutated noninput three-argument primitive leaves:", count)

    def test_cli_and_atomic_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "out.json"
            p.write_text("preserve")
            cmd = [sys.executable, "-m", "argumentlab.ideal_cli"]
            r = subprocess.run(
                cmd + ["-", "--output", str(p)],
                input="{}",
                text=True,
                capture_output=True,
            )
            self.assertEqual(r.returncode, 2)
            self.assertEqual(p.read_text(), "preserve")
            data = controls()[0]["framework"]
            r = subprocess.run(
                cmd + ["-"], input=json.dumps(data), text=True, capture_output=True
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            report = json.loads(r.stdout)
            self.assertEqual(report, audit_ideal(data))
            r = subprocess.run(
                cmd + ["-", "--verify"],
                input=json.dumps(report),
                text=True,
                capture_output=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            for bad in [
                '{"arguments":0,"arguments":0,"attacks":[]}',
                "NaN",
                " " * 65537,
            ]:
                r = subprocess.run(
                    cmd + ["-"], input=bad, text=True, capture_output=True
                )
                self.assertEqual(r.returncode, 2)
                self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
