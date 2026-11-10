"""Installed ideal/eager generation and replay with strict JSON and atomic IO."""

from .ideal import audit_ideal


def main(argv=None):
    """Strict JSON ideal/eager generation/checking with atomic output replacement."""
    import argparse
    import json
    import os
    from pathlib import Path
    import sys
    import tempfile
    from .ideal_verify import verify_ideal

    parser = argparse.ArgumentParser(
        description="Exact finite ideal/eager argumentation cores"
    )
    parser.add_argument("input", help="UTF-8 JSON path or - for stdin")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="independently check an exported ideal/eager report",
    )
    parser.add_argument("-o", "--output")
    args = parser.parse_args(argv)
    limit = 32 * 1024 * 1024 if args.verify else 65536

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    try:
        raw = (
            sys.stdin.buffer.read(limit + 1)
            if args.input == "-"
            else Path(args.input).read_bytes()
        )
        if len(raw) > limit:
            raise ValueError("input exceeds mode UTF-8 byte limit")
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique,
            parse_constant=lambda x: (_ for _ in ()).throw(
                ValueError("nonfinite JSON constant")
            ),
        )
        if args.verify:
            verify_ideal(data)
            result = {"valid": True, "schema": "argumentlab-ideal-v1"}
        else:
            result = audit_ideal(data)
        text = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            target = Path(args.output)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=target.parent, delete=False
            ) as f:
                temporary = f.name
                try:
                    f.write(text)
                except BaseException:
                    os.unlink(temporary)
                    raise
            try:
                os.replace(temporary, target)
            except BaseException:
                os.unlink(temporary)
                raise
        else:
            sys.stdout.write(text)
    except (ValueError, OSError, UnicodeError, RecursionError) as error:
        parser.exit(2, "Invalid input: " + str(error) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
