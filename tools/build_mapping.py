"""
tools/build_mapping.py

Skeleton to build `mapping/post_mapping.csv` from `cs/posts.csv` and scan reports.
This script is intentionally minimal: it reads an input posts CSV and emits a mapping CSV with headers.

Usage:
  python tools/build_mapping.py --posts cs/posts.csv --scan reports/scan_report.json --output mapping/post_mapping.csv

"""
import argparse
import csv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

def build(posts_csv: Path, output_csv: Path):
    rows = []
    with posts_csv.open(encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            source_filename = r.get('post_id')
            # placeholder: real implementation will parse filename/slug
            rows.append({
                'cs_filename': source_filename,
                'en_filename': '',
                'post_numeric_id': '',
                'slug_cs': '',
                'slug_en': '',
                'cs_url': '',
                'en_url': '',
                'translation_status': 'pending'
            })
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    logging.info('Wrote mapping to %s', output_csv)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--posts', required=True)
    ap.add_argument('--scan', required=False)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    build(Path(args.posts), Path(args.output))
