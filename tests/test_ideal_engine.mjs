import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { auditIdeal, parseJSON } from "../docs/ideal-engine.js";
const cases = JSON.parse(
  execFileSync(
    "python",
    [
      "-c",
      "import json;from tools.ideal_cases import controls,exhaustive,seeded;print(json.dumps(list(exhaustive())+seeded()+[c['framework']for c in controls()]))",
    ],
    { maxBuffer: 1e7 },
  ),
);
test("645 full native/independent-checker/JavaScript ideal-eager reports", () => {
  let subsets = 0,
    traces = 0,
    candidates = 0;
  for (let i = 0; i < cases.length; i += 20) {
    const batch = cases.slice(i, i + 20),
      native = JSON.parse(
        execFileSync(
          "python",
          [
            "-c",
            "import json,sys;from argumentlab.ideal import audit_ideal;from argumentlab.ideal_verify import verify_ideal;rs=[audit_ideal(d)for d in json.load(sys.stdin)];assert all(verify_ideal(r)for r in rs);print(json.dumps(rs))",
          ],
          { input: JSON.stringify(batch), maxBuffer: 100e6 },
        ),
      );
    for (let j = 0; j < batch.length; j++) {
      const r = auditIdeal(batch[j]);
      assert.deepEqual(r, native[j], "case " + (i + j));
      subsets += r.subsets.length;
      for (const c of r.cores) {
        traces += c.pruning_trace.length;
        candidates += c.candidates.length;
      }
    }
  }
  console.log(
    JSON.stringify({
      reports: cases.length,
      subsets,
      trace_states: traces,
      candidate_obligations: candidates,
    }),
  );
});
test("strict schema, JSON and no input mutation", () => {
  const d = {
      arguments: 2,
      attacks: [
        [1, 0],
        [0, 1],
      ],
    },
    copy = structuredClone(d);
  auditIdeal(d);
  assert.deepEqual(d, copy);
  for (const x of [
    null,
    [],
    {},
    { ...d, extra: 1 },
    { arguments: true, attacks: [] },
    { arguments: 9, attacks: [] },
    { arguments: 1, attacks: [[false, 0]] },
    {
      arguments: 1,
      attacks: [
        [0, 0],
        [0, 0],
      ],
    },
  ])
    assert.throws(() => auditIdeal(x));
  for (const s of [
    '{"arguments":0,"arguments":0,"attacks":[]}',
    '{"arguments":1.0,"attacks":[]}',
    "NaN",
    " ".repeat(65537),
  ])
    assert.throws(() => parseJSON(s));
});
