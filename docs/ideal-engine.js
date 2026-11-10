/* Independent set-based ideal/eager evidence; no native report is loaded. */
import { validate } from "./engine.js";
export { parseJSON } from "./json-input.js";
const sub = (a, b) => [...a].every((x) => b.has(x)),
  equal = (a, b) => a.size === b.size && sub(a, b),
  strict = (a, b) => a.size < b.size && sub(a, b),
  sorted = (s) => [...s].sort((a, b) => a - b),
  mask = (s) => [...s].reduce((m, a) => m + 2 ** a, 0),
  intersection = (ss) =>
    new Set([...ss[0]].filter((a) => ss.every((s) => s.has(a))));
export function auditIdeal(raw) {
  const framework = validate(raw),
    n = framework.arguments,
    edges = framework.attacks,
    A = new Set(Array.from({ length: n }, (_, a) => a)),
    indices = [...A],
    sets = Array.from(
      { length: 2 ** n },
      (_, m) => new Set(indices.filter((a) => (m >> a) & 1)),
    ),
    incoming = indices.map((a) =>
      edges.filter(([, t]) => t === a).map(([b]) => b),
    );
  const rows = sets.map((s) => {
    const attacked = new Set(edges.filter(([a]) => s.has(a)).map(([, b]) => b)),
      defended = new Set(
        indices.filter((a) => incoming[a].every((b) => attacked.has(b))),
      ),
      conflicts = edges.filter(([a, b]) => s.has(a) && s.has(b)),
      cf = !conflicts.length,
      adm = cf && sub(s, defended),
      defense = indices.map((argument) => {
        const responses = incoming[argument].map((attacker) => ({
            attacker,
            defenders: sorted(
              new Set(
                edges
                  .filter(([d, t]) => t === attacker && s.has(d))
                  .map(([d]) => d),
              ),
            ),
          })),
          unanswered = responses
            .filter((r) => !r.defenders.length)
            .map((r) => r.attacker);
        return {
          argument,
          responses,
          unanswered,
          defended: !unanswered.length,
        };
      });
    return {
      mask: mask(s),
      attacked_mask: mask(attacked),
      range_mask: mask(new Set([...s, ...attacked])),
      defended_mask: mask(defended),
      conflict_free: cf,
      admissible: adm,
      complete: adm && equal(s, defended),
      members: sorted(s),
      conflicts,
      defense,
    };
  });
  const adm = sets.filter((s, i) => rows[i].admissible),
    complete = sets.filter((s, i) => rows[i].complete),
    preferred = adm.filter((s) => !adm.some((t) => strict(s, t))),
    semi = adm.filter(
      (s) =>
        !adm.some((t) =>
          strict(
            sets[rows[mask(s)].range_mask],
            sets[rows[mask(t)].range_mask],
          ),
        ),
    ),
    grounded = complete.filter((s) => !complete.some((t) => strict(t, s))),
    families = {
      complete: complete.map(mask),
      preferred: preferred.map(mask),
      semi_stable: semi.map(mask),
      grounded: grounded.map(mask),
    },
    cores = [];
  for (const [name, parent] of [
    ["ideal", "preferred"],
    ["eager", "semi_stable"],
  ]) {
    const family = families[parent],
      pool = intersection(family.map((m) => sets[m])),
      eligible = adm.filter((s) => sub(s, pool)),
      maximal = eligible.filter((s) => !eligible.some((t) => strict(s, t))),
      union = new Set(eligible.flatMap((s) => [...s])),
      trace = [];
    let current = new Set(pool);
    for (;;) {
      const checks = sorted(current).map((a) => rows[mask(current)].defense[a]),
        removed = new Set(
          checks.filter((c) => !c.defended).map((c) => c.argument),
        ),
        next = new Set([...current].filter((a) => !removed.has(a)));
      trace.push({
        round: trace.length,
        mask: mask(current),
        next_mask: mask(next),
        removed_mask: mask(removed),
        fixed: !removed.size,
        checks,
      });
      if (!removed.size) break;
      current = next;
    }
    const induced = edges.filter(([a, b]) => pool.has(a) && pool.has(b));
    let active = new Set();
    for (;;) {
      const attacked = new Set(
          induced.filter(([a]) => active.has(a)).map(([, b]) => b),
        ),
        next = new Set(
          [...pool].filter((a) =>
            induced.filter(([, t]) => t === a).every(([b]) => attacked.has(b)),
          ),
        );
      if (equal(active, next)) break;
      active = next;
    }
    const candidates = sets.map((s) => ({
        mask: mask(s),
        inside_pool: sub(s, pool),
        eligible: eligible.some((t) => equal(t, s)),
        strict_eligible_supersets: eligible
          .filter((t) => strict(s, t))
          .map(mask),
        subset_of_result: sub(s, union),
      })),
      acceptance = indices.map((argument) => {
        const removal = trace.find((t) => sets[t.removed_mask].has(argument));
        return {
          argument,
          containing_parent_extensions: family.filter((s) =>
            sets[s].has(argument),
          ),
          excluding_parent_extensions: family.filter(
            (s) => !sets[s].has(argument),
          ),
          in_pool: pool.has(argument),
          in_core: union.has(argument),
          removed_round: removal?.round ?? null,
          unanswered_when_removed: removal
            ? rows[removal.mask].defense[argument].unanswered
            : [],
        };
      });
    cores.push({
      semantics: name,
      parent_semantics: parent,
      parent_extensions: family,
      pool_mask: mask(pool),
      pool_admissible: rows[mask(pool)].admissible,
      admissible_subsets: eligible.map(mask),
      maximal_admissible_subsets: maximal.map(mask),
      union_admissible_subsets: mask(union),
      extension_mask: mask(union),
      pruning_trace: trace,
      single_pass_mask: trace[0].next_mask,
      induced_pool_grounded_mask: mask(active),
      candidates,
      acceptance,
    });
    families[name] = [mask(union)];
  }
  const g = sets[families.grounded[0]],
    ideal = sets[families.ideal[0]],
    eager = sets[families.eager[0]];
  return {
    schema: "argumentlab-ideal-v1",
    framework,
    subsets: rows,
    families,
    cores,
    inclusions: {
      grounded_subset_ideal: sub(g, ideal),
      ideal_subset_eager: sub(ideal, eager),
      eager_subset_semistable_intersection: sub(
        eager,
        sets[cores[1].pool_mask],
      ),
    },
    limits: [...LIMITS],
  };
}
const LIMITS = [
  "Finite Dung frameworks with0..8 supplied arguments and a set of directed attacks, including self attacks. Attacks are assumptions, not evidence about real-world truth or argument strength.",
  "Ideal is the greatest admissible subset of every preferred extension. Eager is the greatest admissible subset of every semi-stable extension. Skeptical parent intersection alone need not be admissible.",
  "Preferred and semi-stable parent families are nonempty for these finite frameworks. The zero-argument framework has one empty extension, not an empty family. No arbitrary infinite-framework uniqueness claim.",
  "All defense tests retain the original framework, including attackers outside the intersection pool. Restricting candidate membership does not delete external attackers or induce a new framework.",
  "Simultaneous pruning removes currently undefended pool members until a fixed point. A single pass can be insufficient. Every removed argument retains its unanswered attackers and every response.",
  "All subsets and complete labellings are bounded evidence, not a scalable solver, new theory, dialogue strategy, persuasion model, probability model, semantics ranking or verified AI-agent guarantee.",
];
