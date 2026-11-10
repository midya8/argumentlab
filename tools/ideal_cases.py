"""Original synthetic controls. Seeded discovery is recorded, not copied examples."""

import random


def framework(n, edges):
    return {"arguments": n, "attacks": sorted([list(e) for e in edges])}


def controls():
    cascade = [
        [0, 2],
        [0, 4],
        [1, 1],
        [2, 0],
        [2, 5],
        [2, 6],
        [3, 1],
        [4, 6],
        [5, 0],
        [5, 2],
        [5, 6],
        [6, 3],
        [6, 4],
        [6, 6],
    ]
    xs = [
        (
            "Unanimous does not mean defended",
            "The preferred intersection contains {a3,a4,a7}. Argument a4 first loses defense against a0; then a3 loses its response to a6. The ideal core keeps only a7. Neither one-pass pruning nor deleting outside attackers is valid.",
            8,
            cascade,
        ),
        (
            "A nonempty admissible core",
            "The preferred intersection is {a1,a2}. Only {a1} can stand on its own against every original attacker.",
            6,
            [[0, 2], [0, 4], [3, 0], [3, 4], [3, 5], [4, 0], [4, 3], [4, 5]],
        ),
        (
            "Beyond grounded",
            "A self-attacking attacker prevents grounded acceptance, yet a defended unique preferred position has a larger ideal core.",
            3,
            [[1, 2], [2, 0], [2, 1], [2, 2]],
        ),
        (
            "Eager is not ideal",
            "Range maximality discards one preferred position. The eager core can therefore be larger than the ideal core, without ranking either as universally better.",
            7,
            [
                [1, 2],
                [1, 3],
                [1, 4],
                [1, 5],
                [1, 6],
                [2, 6],
                [3, 0],
                [3, 3],
                [4, 0],
                [4, 3],
                [4, 4],
                [5, 1],
                [5, 2],
                [5, 6],
                [6, 0],
            ],
        ),
        (
            "Unanimous but undefended",
            "Both preferred positions include a0, but they use different defenders. Their shared intersection does not defend a0.",
            6,
            [
                [1, 2],
                [1, 3],
                [1, 5],
                [2, 1],
                [3, 0],
                [4, 2],
                [4, 4],
                [4, 5],
                [5, 3],
                [5, 4],
            ],
        ),
        (
            "Empty framework",
            "There is one empty preferred and semi-stable extension. Empty result does not mean absent parent family.",
            0,
            [],
        ),
        (
            "No attacks",
            "Every argument is unattacked. Both cores, both parent intersections and grounded accept all arguments.",
            3,
            [],
        ),
        (
            "Self attack",
            "A self-attacking argument cannot belong to an admissible position. The nonempty framework still has the empty parent extension.",
            1,
            [[0, 0]],
        ),
        (
            "Mutual alternatives",
            "Two incompatible preferred positions share no argument. The empty core is a legitimate complete extension.",
            2,
            [[0, 1], [1, 0]],
        ),
        (
            "Odd attack cycle",
            "No stable extension exists, but preferred and semi-stable parents do exist. These core computations do not use an empty stable family.",
            3,
            [[0, 1], [1, 2], [2, 0]],
        ),
        (
            "A directed chain",
            "Unattacked acceptance propagates through defense. Both unique cores agree with grounded here.",
            4,
            [[0, 1], [1, 2], [2, 3]],
        ),
        (
            "Every argument self-attacks",
            "No nonempty admissible subset survives. The report retains all original self attacks.",
            4,
            [[i, i] for i in range(4)],
        ),
        (
            "Three pairwise alternatives",
            "Three mutually attacking arguments produce three preferred positions and an empty unanimous pool.",
            3,
            [[a, b] for a in range(3) for b in range(3) if a != b],
        ),
        (
            "The cascade without the survivor",
            "Two pruning rounds remove the entire skeptical pool. Simultaneous rounds are not collapsed into a fabricated one-step justification.",
            7,
            cascade,
        ),
    ]
    return [
        {"name": name, "why": why, "framework": framework(n, edges)}
        for name, why, n, edges in xs
    ]


def exhaustive():
    for n in range(4):
        for bits in range(2 ** (n * n)):
            yield framework(
                n,
                [[a, b] for a in range(n) for b in range(n) if bits >> (a * n + b) & 1],
            )


def seeded(count=100):
    rng = random.Random(72035)
    return [
        framework(
            n, [[a, b] for a in range(n) for b in range(n) if rng.random() < 0.27]
        )
        for n in [rng.randrange(4, 9) for _ in range(count)]
    ]


if __name__ == "__main__":
    import json
    from pathlib import Path

    Path("docs/ideal-controls.json").write_text(json.dumps(controls(), indent=2) + "\n")
    Path("examples/ideal.json").write_text(
        json.dumps(controls()[0]["framework"], indent=2) + "\n"
    )
