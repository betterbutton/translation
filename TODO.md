## Plan: Překlad českého blogu

Krátké shrnutí: Přeložíme obsah ve `cs` do angličtiny bez změny zdrojových souborů; vytvoříme paralelní strom `en`, vygenerujeme mapu `post_id_cs→post_id_en`, přepíšeme odkazy na `better-button.com` a připravíme export pro Substack (HTML/Markdown + metadatové CSV).

### Steps
1. Naskenuj repozitář a ověř strukturu: `cs` a `cs/posts.csv`.
2. Vygeneruj mapu postů: `post_mapping.csv` (format viz sekce Mapping).
3. Napiš skript `scan_and_report.py` pro identifikaci textových uzlů a atributů v `cs/posts/*.html`.
4. Implementuj `translate_html.py` používající HTML parser a DeepL/Google/OpenAI API; zajisti, aby parser zachoval HTML tagy, atributy a embedy.
5. Napiš `rewrite_links.py` — přepíše odkazy z `reknisioweb.cz` → `better-button.com` podle mapy `post_mapping.csv` a doplní `post_id_cs` jako referenci.
6. Dávkově spusť překlad do nové složky `en/`, spusť QA kontrolní skript `qa_checks.py` a vygeneruj adresář `substack_import/` s exportem (HTML/CSV) připraveným pro import do Substack.

### Mapping
- Formát CSV: `source_filename,target_filename,post_id_cs,slug_cs,post_id_en,slug_en,source_url,target_url,translation_status`
- `source_filename`: název souboru ve `cs` (např. `146260790.proc-vynechavame-vyzkum.html`).
- `target_filename`: cílový název souboru v `en` (zachovat `postid.` + přeložený slug), např. `146260790.why-do-we-skip-research.html`.
- `post_id_cs`: numerická část před tečkou z `source_filename`.
- `slug_cs`: část za tečkou v `source_filename`.
- `post_id_en`: numerická část pro anglickou verzi (obvykle shodná s `post_id_cs`).
- `slug_en`: přeložený slug (pomlčky místo mezer, anglický lowercase).
- `source_url` / `target_url`: plné URL pro referenci (volitelné, doporučené pro přepis odkazů).
- `translation_status`: `pending|in_progress|done|review`.

Příklad (CSV header + příklad řádku):
```
source_filename,target_filename,post_id_cs,slug_cs,post_id_en,slug_en,source_url,target_url,translation_status
146260790.proc-vynechavame-vyzkum.html,146260790.why-do-we-skip-research.html,146260790,proc-vynechavame-vyzkum,146260790,why-do-we-skip-research,https://reknisioweb.cz/posts/146260790.proc-vynechavame-vyzkum.html,https://better-button.com/posts/146260790.why-do-we-skip-research.html,done
```

Krátké zobrazení mapování souborů:
- `146260790.proc-vynechavame-vyzkum.html -> 146260790.why-do-we-skip-research.html`

### Zachování integrity HTML
- Překládat pouze textové uzly a vybrané atributy (`alt`, `figcaption`, `title`), nepřepisovat HTML tagy, atributy obsahující URL, data-* atributy, inline skripty a JSON-LD.
- Embed komponenty (`iframe`, `youtube-wrap`, digest embeds) označit jako "do not translate" a zachovat jejich obsah beze změny.

### QA & Reviews
- Po dávkovém překladu spustit `qa_checks.py` který ověří:
  - Nekomprimované/poškozené tagy (neschválené změny v HTML stromu).
  - Přítomnost nenadálých referencí na `reknisioweb.cz`.
  - Překlad délky titulků a přítomnost diakritiky v anglickém textu.
- Bilingvní kontrola: vybrat 10% přeložených postů pro manuální revizi.

### Překladové enginy (doporučení)
- DeepL: nejlepší kvalita pro technické i konverzační texty; dražší, limity na znaky na požádání.
- Google Translate API: škálovatelné, dobrá cena/throughput, méně přesné u idiomů.
- OpenAI (text models): výborná kontextová kvalita a flexibilita (kontrola stylu), vyšší cena za tokeny — vhodné pro finální copyedit.

### Odhady
- Počet HTML: ~1192 (zdrojové odhady).
- Odhadovaný rozsah textu (konzervativně): 400–800 kB čistého textu → API náklady závislé na vybraném poskytovateli; odhad pro DeepL: řádově stovky dolarů; pro Google/omezené použití může být levnější.
- Vývoj skriptů: 1.5–3 dny (pro robustní pipeline s QA). Dávkový běh a kontrola: 1–2 dny.

### Artefakty / Skripty
- `tools/scan_and_report.py` — vstup: `cs/posts/*.html`, výstup: `reports/scan_report.json`; účel: identifikovat textové uzly, odkazy, obrázky s alt, embedy.
- `tools/build_mapping.py` — vstup: `cs/posts.csv` + scan report, výstup: `mapping/post_mapping.csv`.
- `tools/translate_html.py` — vstup: single HTML + mapping, výstup: `en/<same-filename>.html`.
- `tools/rewrite_links.py` — vstup: `en/*.html` + `mapping/post_mapping.csv`, výstup: updated `en/*.html` s přepsanými odkazy.
- `tools/qa_checks.py` — vstup: `en/*.html`, výstup: `reports/qa_report.json`.
- `substack/generate_import.py` — vstup: `en/*.html` + metadata, výstup: `substack_import/` připravené pro import.

### Non-destructive workflow
- `cs/` zůstává read-only; všechna výstupní data jdou do `en/`, `mapping/`, `reports/`, `substack_import/`.
- Návrh názvů pro anglické soubory: zachovat `postid.slug.html` s přeloženým slugem jako `postid.translated-slug.html`.

### Další kroky (rychlý checklist)
1. Vytvořit `tools/scan_and_report.py` a spustit scan na vzorku 50 souborů.
2. Vygenerovat `mapping/post_mapping.csv` automaticky pro všechny soubory.
3. Implementovat překladový krok pro 10 postů jako pilot.
4. QA a manuální revize pilotního batch.
5. Dávkový překlad a export pro Substack.

---

Autor: Martin
Datum: 2026-02-08

