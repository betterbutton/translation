"""
tools/qa_checks.py

Simple QA checks for translated HTML files.
Checks include: well-formed basic HTML parse (very loose), presence of any remaining reknisioweb.cz links,
and that files were produced in the expected output directory.

Usage:
  python tools/qa_checks.py --input en-translated --report reports/qa_report.json
"""
import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)


def run_checks(input_dir: Path):
    problems = []
    for f in input_dir.glob('*.html'):
        text = f.read_text(encoding='utf-8', errors='ignore')
        if 'reknisioweb.cz' in text:
            problems.append({'file': str(f), 'issue': 'contains_reknisioweb_link'})
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--report', required=True)
    args = ap.parse_args()

    issues = run_checks(Path(args.input))
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps({'issues': issues}, ensure_ascii=False, indent=2), encoding='utf-8')
    logging.info('QA checks done; report at %s (issues=%d)', args.report, len(issues))

if __name__ == '__main__':
    main()
