Tools README

This folder contains skeleton utilities for the translation pipeline.

Files:
- `scan_and_report.py`  : Scan `cs/posts/*.html` for links and image alts. Produces `reports/scan_report.json`.
- `build_mapping.py`   : Build an initial `mapping/post_mapping.csv` from `cs/posts.csv` and scan results.
- `translate_html.py`  : Translate HTML content (skeleton placeholder). Writes to `en-translated/`.
- `rename_files.py`    : Rename translated files according to mapping and produce `en-renamed/`.
- `rewrite_links.py`   : Apply `link_mapping.csv` to `en-renamed/` and produce `en-rewritten/`.
- `qa_checks.py`       : Basic QA checks (left as simple examples).

Usage examples are in `TODO.md`.

Next steps:
- Implement robust HTML parsing and text-node-only translation in `translate_html.py`.
- Hook a translation API (DeepL/Google/OpenAI) with batching and rate-limiting.
- Improve `rewrite_links.py` to parse HTML and replace only href values (not blind text replace).
- Add unit tests for each tool.
