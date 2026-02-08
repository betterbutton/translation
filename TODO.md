## Plan: Překlad českého blogu

Krátké shrnutí: Přeložíme obsah ve `cs` do angličtiny bez změny zdrojových souborů; vytvoříme paralelní strom `en`, vygenerujeme mapu `post_id_cs→post_id_en`, přepíšeme odkazy na `better-button.com` a připravíme export pro Substack (HTML/Markdown + metadatové CSV).

### Mapping
- Formát CSV: `source_filename,target_filename,post_numeric_id,slug_cs,slug_en,source_url,target_url,translation_status`
- `source_filename`: název souboru ve `cs` (např. `146260790.proc-vynechavame-vyzkum.html`).
- `target_filename`: cílový název souboru v `en` (zachovat `postid.` + přeložený slug), např. `146260790.why-do-we-skip-research.html`.
- `post_numeric_id`: numerická část před tečkou z `source_filename` (např. `146260790`). Tento sloupec bude použit pro jednoznačné párování mezi zdrojem a překladem; hodnoty pro zdroj i cíl jsou shodné.
- `slug_cs`: část za tečkou v `source_filename` (původní český slug).
- `slug_en`: přeložený slug pro cílové URL (pomlčky místo mezer, anglický lowercase).
- `source_url`: plná URL ve formátu `https://www.reknisioweb.cz/p/` + `slug_cs` (při skládání i varianty bez `www.` mohou v HTML výskytech existovat — scan by je měl detekovat).
- `target_url`: plná URL ve formátu `https://www.better-button.com/p/` + `slug_en`.
- `translation_status`: `pending|in_progress|done|review`.

Příklad (CSV header + příklad řádku):
```
source_filename,target_filename,post_numeric_id,slug_cs,slug_en,source_url,target_url,translation_status
146260790.proc-vynechavame-vyzkum.html,146260790.why-do-we-skip-research.html,146260790,proc-vynechavame-vyzkum,why-do-we-skip-research,https://www.reknisioweb.cz/p/proc-vynechavame-vyzkum,https://www.better-button.com/p/why-do-we-skip-research,done
```

Krátké zobrazení mapování souborů:
- `146260790.proc-vynechavame-vyzkum.html -> 146260790.why-do-we-skip-research.html`

### Link mapping (pro přepis odkazů uvnitř HTML)
- Některé odkazy v HTML nebudou přesně odpovídat patternu pro posty (mohou odkazovat na kategorie, feedy, stránky s query stringy nebo externí zdroje). Proto vytvoříme samostatnou mapu pro přepis odkazů.
- Formát CSV: `source_filename,target_filename,source_link,target_link`
  - `source_filename`: soubor, ve kterém se odkaz vyskytl.
  - `target_filename`: cílový soubor po překladu (pokud odkaz směřuje na přeložený post); může být prázdné pro odkazy, které nepřekládáme.
  - `source_link`: přesná URL, jak se vyskytuje v HTML (detekovat varianty s/bez `www.`, `http`/`https`, trailing slashes, UTM parametry apod.).
  - `target_link`: canonical cílová URL pro přepis v `en` (pokud existuje) — pro posty musí mít strukturu `https://www.better-button.com/p/` + `slug_en`.

  - Požadavky a zásady:
    - Každý unikátní `source_link` musí mapovat na unikátní `target_link` (konzistence pro přepis napříč soubory).
    - Pokud `source_link` odkazuje na post, `target_link` musí respektovat `post_numeric_id` a `slug_en` z hlavního mapovacího CSV.
    - Pokud se `source_link` vyskytuje s různými query parametry nebo protokoly, normalizovat `source_link` pro klíčování a zachovat původní varianty v poznámce.

Příklad řádku `link_mapping.csv`:
```
source_filename,target_filename,source_link,target_link
141177637.konference-2024.html,141177637.conferences-2024,https://reknisioweb.cz/p/konference-2024-01,https://www.better-button.com/p/konference-2024-01
```

Scan požadavky:
- Před provedením přepisu odkazů spustit `tools/scan_and_report.py` na všech `cs/posts/*.html` a extrahovat všechny `href` obsahující `reknisioweb.cz` nebo `reknisioweb.cz` bez `www.`. Označit, které odkazy odpovídají postům (podle slug patternu) a které odkazují na jiné stránky.
- Vygenerovat `link_mapping.csv` s jedinečnými `source_link` a navrhovanými `target_link` (nechat prázdné `target_link` pro odkazy, které nebudou přepisovány automaticky).

Tyto změny zajistí, že přepis odkazů bude deterministický a konzistentní napříč celým archivem.
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

