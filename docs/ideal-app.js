import { auditIdeal, parseJSON } from "./ideal-engine.js";
const $ = (id) => document.getElementById(id),
  el = (tag, text) => {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    return e;
  },
  fmt = (x) => (typeof x === "object" ? JSON.stringify(x) : String(x)),
  yes = (x) => (x ? "yes" : "no");
let controls = [],
  report = null,
  ci = 0;
const members = (s) =>
    Array.from({ length: report.framework.arguments }, (_, a) => a).filter(
      (a) => (s >> a) & 1,
    ),
  show = (s) =>
    "{" +
    members(s)
      .map((a) => "a" + a)
      .join(", ") +
    "}",
  setmask = (s) => s + " / " + show(s);
function table(id, headers, rows) {
  const t = $(id),
    h = el("thead"),
    tr = el("tr"),
    body = el("tbody");
  headers.forEach((x) => {
    const th = el("th", x);
    th.scope = "col";
    tr.append(th);
  });
  h.append(tr);
  for (const data of rows) {
    const row = el("tr");
    if (data.selected) row.className = "selected";
    for (const x of data.cells ?? data) row.append(el("td", fmt(x)));
    body.append(row);
  }
  t.replaceChildren(h, body);
}
function cards(id, rows) {
  $(id).replaceChildren(
    ...rows.map(([heading, fields]) => {
      const c = el("div");
      c.className = "card";
      c.append(el("h3", heading));
      const dl = el("dl");
      for (const [k, v] of fields) dl.append(el("dt", k), el("dd", fmt(v)));
      c.append(dl);
      return c;
    }),
  );
}
function options(id, rows) {
  $(id).replaceChildren(
    ...rows.map(([value, text]) => {
      const o = el("option", text);
      o.value = String(value);
      return o;
    }),
  );
}
function graph(current, removed) {
  const svg = $("graph"),
    NS = "http://www.w3.org/2000/svg",
    add = (tag, attrs, parent = svg) => {
      const e = document.createElementNS(NS, tag);
      for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
      parent.append(e);
      return e;
    };
  svg.replaceChildren();
  const defs = add("defs", {}),
    marker = add(
      "marker",
      {
        id: "ideal-arrow",
        viewBox: "0 0 10 10",
        refX: 9,
        refY: 5,
        markerWidth: 7,
        markerHeight: 7,
        orient: "auto",
      },
      defs,
    );
  add("path", { d: "M0,0 L10,5 L0,10 z", fill: "#758a8b" }, marker);
  const n = report.framework.arguments,
    ids = Array.from({ length: n }, (_, a) => a),
    points = ids.map((a, i) => {
      const angle = -Math.PI / 2 + (2 * Math.PI * i) / n;
      return n === 1
        ? [200, 210]
        : [200 + 130 * Math.cos(angle), 210 + 130 * Math.sin(angle)];
    });
  if (!n) add("text", { x: 200, y: 200 }).textContent = "Empty graph";
  for (const [a, b] of report.framework.attacks) {
    const [x, y] = points[a],
      [u, v] = points[b];
    let d;
    if (a === b)
      d = `M${x - 15},${y - 18} C${x - 65},${y - 90} ${x + 65},${y - 90} ${x + 15},${y - 18}`;
    else {
      const dx = u - x,
        dy = v - y,
        len = Math.hypot(dx, dy),
        sx = x + (27 * dx) / len,
        sy = y + (27 * dy) / len,
        ex = u - (29 * dx) / len,
        ey = v - (29 * dy) / len,
        opp = report.framework.attacks.some(([c, e]) => c === b && e === a);
      d = opp
        ? `M${sx},${sy} Q${(sx + ex) / 2 - (18 * dy) / len},${(sy + ey) / 2 + (18 * dx) / len} ${ex},${ey}`
        : `M${sx},${sy} L${ex},${ey}`;
    }
    add("path", {
      d,
      class: "edge",
      "marker-end": "url(#ideal-arrow)",
      "data-source": a,
      "data-target": b,
    });
  }
  for (const a of ids) {
    const [x, y] = points[a],
      selected = Boolean((current >> a) & 1),
      lost = Boolean((removed >> a) & 1),
      g = add("g", {
        "data-argument": a,
        "data-selected": selected,
        "data-removed": lost,
      });
    if (lost) add("circle", { cx: x, cy: y, r: 31, class: "removed-ring" }, g);
    add(
      "circle",
      { cx: x, cy: y, r: 25, class: selected ? "selected" : "outside" },
      g,
    );
    add("text", { x, y }, g).textContent = "a" + a;
    add("title", {}, g).textContent =
      "a" +
      a +
      ": " +
      (selected ? "in current position" : "outside current position") +
      (lost ? ", removed this round" : "");
  }
}
function defense(row, selectedOnly = false) {
  return row.defense
    .filter((d) => !selectedOnly || (row.mask >> d.argument) & 1)
    .map((d) => [
      "a" + d.argument,
      yes(Boolean((row.mask >> d.argument) & 1)),
      d.responses
        .map(
          (x) =>
            "a" +
            x.attacker +
            " ← " +
            (x.defenders.map((a) => "a" + a).join(", ") || "no response"),
        )
        .join("; ") || "unattacked",
      d.unanswered.map((a) => "a" + a).join(", ") || "none",
      yes(d.defended),
    ]);
}
function round() {
  if (!report) return;
  const c = report.cores[ci],
    t = c.pruning_trace[Number($("round").value)];
  cards("round-summary", [
    [
      "This simultaneous round",
      [
        ["Current position", setmask(t.mask)],
        ["Remove now", setmask(t.removed_mask)],
        ["Next position", setmask(t.next_mask)],
        ["Fixed point", yes(t.fixed)],
      ],
    ],
  ]);
  $("round-note").textContent = t.fixed
    ? "Every remaining member is defended. This conflict-free fixed point is the greatest admissible subset of the parent intersection."
    : "Remove all currently undefended members together. A defender lost in this round can cause a different member to fail in the next round.";
  table(
    "round-defense",
    [
      "Argument",
      "Selected",
      "Original attacker ← current responses",
      "Unanswered attackers",
      "Defended",
    ],
    defense(report.subsets[t.mask], true),
  );
  graph(t.mask, t.removed_mask);
}
function candidate() {
  if (!report) return;
  const c = report.cores[ci],
    mask = Number($("candidate").value),
    row = report.subsets[mask],
    x = c.candidates[mask];
  cards("candidate-summary", [
    [
      "Selected alternative",
      [
        ["Mask / members", setmask(mask)],
        ["Inside parent intersection", yes(x.inside_pool)],
        ["Conflict edges", row.conflicts],
        ["Admissible on original graph", yes(row.admissible)],
      ],
    ],
    [
      "Its exact core obligation",
      [
        ["Eligible: inside pool and admissible", yes(x.eligible)],
        ["Strict eligible superset masks", x.strict_eligible_supersets],
        ["Contained in greatest core", yes(x.subset_of_result)],
        ["The unique maximal eligible mask", c.maximal_admissible_subsets],
      ],
    ],
  ]);
  table(
    "candidate-defense",
    [
      "Argument",
      "Selected",
      "Original attacker ← selected responses",
      "Unanswered attackers",
      "Defended",
    ],
    defense(row),
  );
  $("candidate-json").textContent = JSON.stringify(
    { subset: row, obligation: x },
    null,
    2,
  );
  table(
    "atlas",
    [
      "Mask",
      "Inside pool",
      "Admissible",
      "Eligible",
      "Strict eligible supersets",
      "Subset of result",
    ],
    c.candidates.map((x) => ({
      selected: x.mask === mask,
      cells: [
        x.mask,
        yes(x.inside_pool),
        yes(report.subsets[x.mask].admissible),
        yes(x.eligible),
        x.strict_eligible_supersets,
        yes(x.subset_of_result),
      ],
    })),
  );
}
function core() {
  if (!report) return;
  const c = report.cores[ci];
  $("ideal").setAttribute("aria-pressed", String(ci === 0));
  $("eager").setAttribute("aria-pressed", String(ci === 1));
  cards("core-summary", [
    [
      "The " + c.parent_semantics + " intersection",
      [
        ["Parent extension masks", c.parent_extensions],
        ["Every parent contains", setmask(c.pool_mask)],
        ["Intersection admissible", yes(c.pool_admissible)],
      ],
    ],
    [
      "The " + c.semantics + " core",
      [
        ["Greatest admissible position", setmask(c.extension_mask)],
        ["All eligible subset masks", c.admissible_subsets],
        ["Grounded for comparison", setmask(report.families.grounded[0])],
      ],
    ],
  ]);
  $("contrast").textContent =
    "After one pass: " +
    show(c.single_pass_mask) +
    ". After convergence: " +
    show(c.extension_mask) +
    ". Grounded on the incorrectly induced pool graph: " +
    show(c.induced_pool_grounded_mask) +
    ". " +
    (c.induced_pool_grounded_mask === c.extension_mask
      ? "That last shortcut happens to agree here; it is not the definition."
      : "Deleting external attackers changes the answer.");
  options(
    "round",
    c.pruning_trace.map((t) => [
      t.round,
      "Round " +
        t.round +
        " / " +
        show(t.mask) +
        (t.fixed ? " / fixed point" : " / removes " + show(t.removed_mask)),
    ]),
  );
  $("round").value = "0";
  options(
    "candidate",
    report.subsets.map((r) => [r.mask, setmask(r.mask)]),
  );
  $("candidate").value = String(c.pool_mask);
  table(
    "trace-table",
    ["Round", "Current mask / members", "Remove", "Next", "Fixed"],
    c.pruning_trace.map((t) => [
      t.round,
      setmask(t.mask),
      setmask(t.removed_mask),
      setmask(t.next_mask),
      yes(t.fixed),
    ]),
  );
  table(
    "acceptance",
    [
      "Argument",
      "Containing parent masks",
      "Excluding parent masks",
      "In intersection",
      "In core",
      "Removal round",
      "Unanswered at removal",
    ],
    c.acceptance.map((a) => [
      "a" + a.argument,
      a.containing_parent_extensions,
      a.excluding_parent_extensions,
      yes(a.in_pool),
      yes(a.in_core),
      a.removed_round ?? "not removed",
      a.unanswered_when_removed,
    ]),
  );
  round();
  candidate();
}
function clear() {
  report = null;
  window.currentIdealReport = null;
  $("results").hidden = true;
  $("export").disabled = true;
  for (const node of document.querySelectorAll(
    "#results table,#results .cards,#graph,#report-json,#candidate-json",
  ))
    node.replaceChildren();
  $("status").textContent = "Input changed. Run the inspector again.";
}
function run() {
  clear();
  try {
    report = auditIdeal(parseJSON($("input").value));
    window.currentIdealReport = report;
    ci = 0;
    $("results").hidden = false;
    $("export").disabled = false;
    $("status").textContent =
      "Complete finite core audit: " +
      report.subsets.length +
      " subsets, both parent families and both descending traces.";
    cards(
      "families",
      ["preferred", "semi_stable", "grounded", "ideal", "eager"].map((k) => [
        k,
        [
          ["All extension masks", report.families[k]],
          ["Extensions as positions", report.families[k].map(show).join(" ; ")],
        ],
      ]),
    );
    $("inclusions").textContent =
      "Grounded ⊆ ideal ⊆ eager ⊆ every semi-stable extension. Every inclusion is checked on this supplied finite graph. Inclusion can be strict; none of these is a universal semantics ranking.";
    $("limits").replaceChildren(...report.limits.map((x) => el("li", x)));
    $("report-json").textContent = JSON.stringify(report, null, 2);
    core();
  } catch (e) {
    clear();
    $("status").textContent = "Invalid input: " + e.message;
  }
}
function control() {
  const c = controls[Number($("control").value)];
  $("control-note").textContent = c.why;
  $("input").value = JSON.stringify(c.framework, null, 2);
  run();
}
$("control").addEventListener("change", control);
$("input").addEventListener("input", clear);
$("run").addEventListener("click", run);
$("round").addEventListener("change", round);
$("candidate").addEventListener("change", candidate);
for (const [id, i] of [
  ["ideal", 0],
  ["eager", 1],
])
  $(id).addEventListener("click", () => {
    ci = i;
    core();
  });
$("export").addEventListener("click", () => {
  if (!report) return;
  const url = URL.createObjectURL(
      new Blob([JSON.stringify(report, null, 2) + "\n"], {
        type: "application/json",
      }),
    ),
    a = el("a");
  a.href = url;
  a.download = "argumentlab-ideal.json";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
try {
  const r = await fetch("ideal-controls.json");
  if (!r.ok) throw Error("controls unavailable");
  controls = await r.json();
  options(
    "control",
    controls.map((c, i) => [i, c.name]),
  );
  control();
} catch (e) {
  $("status").textContent = "Could not start: " + e.message;
}
