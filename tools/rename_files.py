"""
tools/rename_files.py

Skeleton to rename files in `en-translated/` according to `mapping/post_mapping.csv` and emit into `en-renamed/`.

Usage:
  python tools/rename_files.py --mapping mapping/post_mapping.csv --input en-translated --output en-renamed
"""
import argparse
import csv
from pathlib import Path
import logging
import shutil

logging.basicConfig(level=logging.INFO)


def load_mapping(path: Path):
    rows = {}
    with path.open(encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows[r['cs_filename']] = r
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mapping', required=True)
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    mapping = load_mapping(Path(args.mapping))
    inp = Path(args.input)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    for f in inp.glob('*.html'):
        rec = mapping.get(f.name)
        if rec and rec.get('en_filename'):
            target = out / rec['en_filename']
        else:
            target = out / f.name
        logging.info('Copy %s -> %s', f.name, target.name)
        shutil.copy2(f, target)

    logging.info('Rename/copy step completed')

if __name__ == '__main__':
    main()
