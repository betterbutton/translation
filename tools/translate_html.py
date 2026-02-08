"""
tools/translate_html.py

Skeleton for HTML translation step. This script should accept an input directory of HTML files and
produce translated HTML files into an output directory while preserving HTML structure.

This skeleton only copies files and marks TODOs where integration with a translation API should happen.

Usage:
  python tools/translate_html.py --input cs/posts --output en-translated --batch 10
"""
import argparse
import logging
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)


def translate_file(src: Path, dst: Path):
    # TODO: parse HTML and translate only text nodes and selected attributes
    # For now, copy file as placeholder
    dst.write_text(src.read_text(encoding='utf-8', errors='ignore'), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--batch', type=int, default=0)
    args = ap.parse_args()

    src_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = list(src_dir.glob('*.html'))
    if args.batch and args.batch > 0:
        files = files[: args.batch]

    for f in files:
        dst = out_dir / f.name
        logging.info('Translating %s -> %s', f.name, dst)
        translate_file(f, dst)

    logging.info('Translation placeholder completed')


if __name__ == '__main__':
    main()
