"""Inspect a finite abstract argumentation framework."""
import argparse
import json
from pathlib import Path
from .core import audit, parse

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input');ap.add_argument('--output');args=ap.parse_args()
    try:
        report=audit(parse(Path(args.input).read_text()));text=json.dumps(report,indent=2)+'\n'
        if args.output:Path(args.output).write_text(text)
        else:print(text,end='')
    except (ValueError,OSError) as exc:ap.exit(2,f'Invalid input: {exc}\n')
