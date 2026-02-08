NEXT STEPS — Resume instructions (created 2026-02-08)

Status (end of day):
- Remote repo created: https://github.com/betterbutton/translation (branch: `main`).
- `TODO.md` updated with mapping, normalization, slug rules, phased non-destructive workflow.
- `tools/` created with skeleton scripts:
  - `tools/scan_and_report.py` (scan HTML links/alt)
  - `tools/build_mapping.py` (create mapping CSV)
  - `tools/translate_html.py` (translate HTML placeholder)
  - `tools/rename_files.py` (rename according to mapping)
  - `tools/rewrite_links.py` (apply link mapping)
  - `tools/qa_checks.py` (basic QA checks)
- `TODO.md` uses final folder `en-rewritten` for rewritten outputs.

Priority tasks for tomorrow (recommended order):
1) Run a sample scan (50 files) to collect real link data
   - Command:
     ```powershell
     python tools/scan_and_report.py --input cs/posts --output reports/scan_report.json --sample 50
     ```
   - Output: `reports/scan_report.json` (use to populate `link_mapping.csv` and check non-post links).

2) Build initial `mapping/post_mapping.csv` from `cs/posts.csv` (pilot 50 posts)
   - Command:
     ```powershell
     python tools/build_mapping.py --posts cs/posts.csv --scan reports/scan_report.json --output mapping/post_mapping.csv
     ```
   - Manual step: review `mapping/post_mapping.csv` and fill `slug_en`/`en_filename` for pilot posts (or implement automated slug generation from `title_en`).

3) Translate a pilot batch (10 posts) into `en-translated/` and produce `en-translated/posts.csv` with `title_en` and `subtitle_en`.
   - Command:
     ```powershell
     python tools/translate_html.py --input cs/posts --output en-translated --batch 10
     ```
   - Next: run `tools/qa_checks.py --input en-translated --report reports/qa_phase1.json` and inspect issues.

4) Generate slugs and run rename step to `en-renamed/`.
   - Command:
     ```powershell
     python tools/build_mapping.py --posts en-translated/posts.csv --output mapping/post_mapping.csv
     python tools/rename_files.py --mapping mapping/post_mapping.csv --input en-translated --output en-renamed
     ```

5) Prepare `link_mapping.csv` (populate `en_link` for post links; set `action=review` for others), then run rewrite to `en-rewritten/`.
   - Command:
     ```powershell
     python tools/rewrite_links.py --mapping mapping/link_mapping.csv --input en-renamed --output en-rewritten
     ```

6) Final QA and prepare `substack_import/` (use `substack/generate_import.py` when ready).

Notes & important environment setup:
- Translation API credentials must be set in environment variables before running real translations (DeepL/Google/OpenAI). Do not commit credentials.
- For slug generation: use `title_en` (after translation) to derive `slug_en` with allowed characters: a-z, 0-9, and hyphens only.
- Keep `cs/` unchanged; all outputs go to `en-translated/`, `en-renamed/`, `en-rewritten/`, `mapping/`, `reports/`, `substack_import/`.

Files to inspect first tomorrow:
- `TODO.md` (root) — verify rules and mapping format.
- `tools/scan_and_report.py` — run on sample to collect `cs_link` occurrences.
- `cs/posts.csv` and `cs/posts/` sample HTMLs (already present).

If you want, tomorrow I can:
- Run the sample scan and open `reports/scan_report.json` for review.
- Implement text-node-only HTML parsing in `tools/translate_html.py` and wire a translation API (requires credentials).

End of day — pa! (I'll be ready to continue with the first scan when you say go.)
