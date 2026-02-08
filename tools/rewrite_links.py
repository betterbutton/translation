"""
tools/rewrite_links.py

Skeleton that applies `link_mapping.csv` to files in input dir and writes rewritten files to output dir.

Usage:
  python tools/rewrite_links.py --mapping mapping/link_mapping.csv --input en-renamed --output en-rewritten
"""
import argparse
import csv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)


def load_link_map(path: Path):
    m = {}
    with path.open(encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            norm = r.get('normalized_cs_link') or r.get('cs_link')
            if norm:
                m[norm] = r
    return m


def rewrite_file(path: Path, linkmap: dict, outpath: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    # NOTE: This is a placeholder. Proper implementation should parse HTML and replace href values only.
    for norm, rec in linkmap.items():
        src = rec.get('cs_link')
        target = rec.get('en_link') or ''
        if src and target:
            text = text.replace(src, target)
    outpath.write_text(text, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mapping', required=True)
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    linkmap = load_link_map(Path(args.mapping))
    inp = Path(args.input)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    for f in inp.glob('*.html'):
        dst = out / f.name
        logging.info('Rewriting %s -> %s', f.name, dst.name)
        rewrite_file(f, linkmap, dst)

    logging.info('Rewrite links placeholder completed')

if __name__ == '__main__':
    main()
