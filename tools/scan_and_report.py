"""
tools/scan_and_report.py

Small utility to scan `cs/posts/*.html` and collect metadata useful for mapping and link-rewrite.
This is a runnable skeleton: it will walk input directory, parse HTML files for <a href> and <img alt> occurrences
and emit a JSON report. Implementation is intentionally small and dependency-free.

Usage:
  python tools/scan_and_report.py --input cs/posts --output reports/scan_report.json --sample 50

"""
import argparse
import json
import logging
from pathlib import Path
from html.parser import HTMLParser

logging.basicConfig(level=logging.INFO)

class LinkAltParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.alts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'img':
            self.alts.append(attrs.get('alt', ''))


def scan_file(path: Path):
    parser = LinkAltParser()
    data = path.read_text(encoding='utf-8', errors='ignore')
    parser.feed(data)
    return {
        'file': str(path),
        'links': parser.links,
        'alts': parser.alts[:3]
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--sample', type=int, default=50)
    args = ap.parse_args()

    input_dir = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    files = list(input_dir.glob('*.html'))
    logging.info('Found %d html files in %s', len(files), input_dir)

    results = []
    for i, f in enumerate(files[: args.sample]):
        logging.info('Scanning %s', f.name)
        results.append(scan_file(f))

    report = {
        'scanned': len(results),
        'samples': results
    }

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    logging.info('Wrote scan report to %s', out_path)


if __name__ == '__main__':
    main()
