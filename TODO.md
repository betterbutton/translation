## Plan: Překlad českého blogu

Krátké shrnutí: Přeložíme obsah ve `cs` do angličtiny bez změny zdrojových souborů; vytvoříme paralelní strom `en`, vygenerujeme mapu `slug_cs→slug_en`, přepíšeme odkazy na `better-button.com` a připravíme export pro Substack (HTML/Markdown + metadatové CSV).

### Mapping
- Formát CSV: `cs_filename,en_filename,post_numeric_id,slug_cs,slug_en,cs_url,en_url,translation_status`
- `cs_filename`: název souboru ve `cs` (např. `146260790.proc-vynechavame-vyzkum.html`).
- `en_filename`: cílový název souboru v `en` (zachovat `postid.` + přeložený slug), např. `146260790.why-do-we-skip-research.html`.
- `post_numeric_id`: numerická část před tečkou z `cs_filename` (např. `146260790`). Tento sloupec bude použit pro jednoznačné párování mezi zdrojem a překladem; hodnoty pro zdroj i cíl jsou shodné.
- `slug_cs`: část za tečkou v `cs_filename` (původní český slug).
- `slug_en`: přeložený slug pro cílové URL (pomlčky místo mezer, anglický lowercase).
- `cs_url`: plná URL ve formátu `https://www.reknisioweb.cz/p/` + `slug_cs` (při skládání i varianty bez `www.` mohou v HTML výskytech existovat — scan by je měl detekovat).
- `en_url`: plná URL ve formátu `https://www.better-button.com/p/` + `slug_en`.
- `translation_status`: `pending|in_progress|done|review`.

Příklad (CSV header + příklad řádku):
```
cs_filename,en_filename,post_numeric_id,slug_cs,slug_en,cs_url,en_url,translation_status
146260790.proc-vynechavame-vyzkum.html,146260790.why-do-we-skip-research.html,146260790,proc-vynechavame-vyzkum,why-do-we-skip-research,https://www.reknisioweb.cz/p/proc-vynechavame-vyzkum,https://www.better-button.com/p/why-do-we-skip-research,done
```

Krátké zobrazení mapování souborů:
- `146260790.proc-vynechavame-vyzkum.html -> 146260790.why-do-we-skip-research.html`

### Link mapping (pro přepis odkazů uvnitř HTML)
- V HTML souborech budeme detekovat odkazy obsahující doménu `reknisioweb.cz` (varianty s/bez `www.`). Takové odkazy zapíšeme do samostatné mapy `link_mapping.csv`.
- Pokud `cs_link` odkazuje na post (cesta má tvar `/p/<slug_cs>`), `en_link` musí být canonicalní `en_url` podle hlavního mapovacího CSV (viz `cs_filename` ↔ `en_filename` mapování). Pokud `cs_link` neodkazuje na post (např. kategorie, feed, externí stránka), `en_link` necháme prázdné a nastavíme `action=review`.
- Formát CSV: `cs_filename,en_filename,cs_link,normalized_cs_link,en_link,action,notes`
  - `cs_filename`: český soubor, ve kterém se odkaz vyskytl.
  - `en_filename`: anglický soubor po překladu (pokud existuje nebo bude existovat).
  - `cs_link`: přesná URL, jak se vyskytuje v HTML.
  - `normalized_cs_link`: normalizovaná verze `cs_link` pro klíčování (viz Normalizace URL níže).
  - `en_link`: canonical cílová URL pro přepis v `en` (pokud se odkaz přepisuje automaticky) — pro posty má tvar `https://www.better-button.com/p/<slug_en>`.
  - `action`: `map|ignore|review` — u ne-post odkazů se použije `review` a `en_link` zůstane prázdné; pro čisté mapování použít `map`.
  - `notes`: volitelné poznámky o variantách `cs_link` nebo důvodech review.

- Požadavky a zásady:
  - Každý unikátní `normalized_cs_link` musí mapovat na jediný `en_link` (konzistence napříč soubory).
  - Pokud `cs_link` odkazuje na post, `en_link` musí respektovat `post_numeric_id` a `slug_en` z hlavního mapovacího CSV.
  - U ne-post odkazů bude `en_link` prázdné a `action` = `review`.
  - Pokud se `cs_link` vyskytuje s různými query parametry nebo protokoly, normalizovat `cs_link` pro klíčování a zachovat původní varianty v `notes`.

Příklad řádku `link_mapping.csv`:
```
cs_filename,en_filename,cs_link,normalized_cs_link,en_link,action,notes
141177637.konference-2024.html,141177637.conferences-2024,https://reknisioweb.cz/p/konference-2024-01,https://www.reknisioweb.cz/p/konference-2024-01,https://www.better-button.com/p/konference-2024-01,map,
```

Scan požadavky:
- Před provedením přepisu odkazů spustit `tools/scan_and_report.py` na všech `cs/posts/*.html` a extrahovat všechny `href` obsahující `reknisioweb.cz` (s/bez `www.`). Označit, které odkazy odpovídají postům (podle patternu `/p/<slug>`) a které odkazují na jiné stránky.
- Vygenerovat `link_mapping.csv` s jedinečnými `normalized_cs_link` a navrhovanými `en_link` (nechat prázdné `en_link` + `action=review` pro odkazy, které nebudou přepisovány automaticky).

Normalizace URL (pravidla pro `normalized_cs_link` a `en_link` canonical):
- Canonical hosty: použít `https://www.` prefix pro `en_link` (`https://www.better-button.com`) a pro normalized `cs_link` použít `https://www.reknisioweb.cz`.
- Odstranit query parametry a fragmenty (`?` a `#` části) — canonical URL nesmí mít query ani fragment.
- Odstranit trailing slash a souborové přípony (např. `.html`) — canonical cesta bude bez koncového `/`.
- `en_link` musí mít přesnou formu: `https://www.better-button.com/p/<slug_en>` (žádné prefixy, žádné další path segmenty).

Tyto změny zajistí, že přepis odkazů bude deterministický a konzistentní napříč celým archivem.

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

