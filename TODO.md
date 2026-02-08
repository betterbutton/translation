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

### Phased non-destructive workflow (explicitní)
Pro minimalizaci rizika a možnosti rollbacku rozdělíme celý převod do tří fází. Každá fáze má vlastní výstupní adresář a je nezávislá na předchozích fázích.

- Fáze 1 — `en-translated` (překlad obsahu):
  - Vstup: `cs/posts/*.html`, `cs/posts.csv`.
  - Cíl: přeložené HTML soubory uložené do `en-translated/` se stejnými názvy souborů jako v `cs/` (dočasné, zachovávají originální postid a původní slug v názvu souboru).
  - Dále: vytvořit `en-translated/posts.csv` se stejnou strukturou jako `cs/posts.csv`, kde `title` a `subtitle` jsou první přeložené verze (`title_en`, `subtitle_en`). `post_id` v tomto souboru bude dočasný `<post_numeric_id>.<slug_cs>`.
  - Verifikace: spustit `tools/qa_checks.py` pro syntaktické kontroly HTML, kontrolu nezměněných tagů, a kontrolu, že neexistují nevhodné `reknisioweb.cz` odkazy.
  - Rollback: smazat `en-translated/` a znovu spustit překlad.

- Fáze 2 — `en-renamed` (přejmenování podle přeložených titulků):
  - Vstup: `en-translated/`, `en-translated/posts.csv` (přeložené názvy a titulky).
  - Proces: z `title_en` v `en-translated/posts.csv` vygenerovat `slug_en` podle pravidel (malá písmena, pomlčky, číslice). Vytvořit `en-renamed/` kopiemi souborů z `en-translated/`, ale přejmenované na nový `en_filename` (`<post_numeric_id>.<slug_en>.html`).
  - Aktualizace map: v `mapping/post_mapping.csv` doplnit `en_filename`, `slug_en`, `en_url` odpovídající novým názvům.
  - Verifikace: ověřit, že `en-renamed/` soubory odpovídají `en_filename` a že žádné přejmenování nekoliduje (duplicitní slugs). Pokud jsou kolize, označit řádky v `posts.csv` k ručnímu zásahu.
  - Rollback: smazat `en-renamed/` a upravit `en-translated/posts.csv` nebo `posts.csv` a znovu spustit přejmenování.

- Fáze 3 — `en` (přepsání odkazů a finalizace):
  - Vstup: `en-renamed/`, `mapping/post_mapping.csv`, `link_mapping.csv`.
  - Proces: spustit `tools/rewrite_links.py`, který prochází soubory v `en-renamed/`, přepisuje `href` podle `link_mapping.csv` a vytváří výsledné, produkční soubory v `en/`.
  - Výstup: `en/` (finalní publikovatelné HTML), `en/posts.csv` (finalní s `post_id` = `<post_numeric_id>.<slug_en>` a přeloženými `title`/`subtitle`), `substack_import/` připravené pro import.
  - Verifikace: opět `tools/qa_checks.py` (kontrola integrity HTML, testování odkazů, ověření canonical `en_link` formátu). Spustit náhodnou sadu manuálních kontrol (bilingvní QA) nad 10% postů.
  - Rollback: v případě chyb lze znovu vygenerovat `en` z `en-renamed/` nebo obnovit z Git historie; `en-renamed/` a `en-translated/` zůstávají po dobu QA pro audit.

Další poznámky k fázi:
- Každá fáze vytváří mapu změn a reporty v `reports/` (např. `reports/phase1_scan.json`, `reports/phase2_rename.csv`, `reports/phase3_link_check.json`).
- Automatické CI joby by měly běžet pouze na souborech v dané fázi a nikdy nepřepisovat `cs/`.
- Doporučené příkazy pro lokální běh (příklad):
```powershell
# Fáze 1: překlad (pilotní vzorek)
python tools/translate_html.py --input cs/posts --output en-translated --batch 10

# Fáze 2: přejmenování podle přeložených titles
python tools/build_mapping.py --posts en-translated/posts.csv --output mapping/post_mapping.csv
python tools/rename_files.py --mapping mapping/post_mapping.csv --input en-translated --output en-renamed

# Fáze 3: přepis odkazů a export pro Substack
python tools/rewrite_links.py --mapping mapping/link_mapping.csv --input en-renamed --output en
python substack/generate_import.py --input en --posts en/posts.csv --output substack_import
```

Tento fázovaný přístup minimalizuje riziko a umožní postupné kontroly a rollbacky mezi fázemi.

### Další kroky (rychlý checklist)
1. Vytvořit `tools/scan_and_report.py` a spustit scan na vzorku 50 souborů.
2. Vygenerovat `mapping/post_mapping.csv` automaticky pro všechny soubory.
3. Implementovat překladový krok pro 10 postů jako pilot.
4. QA a manuální revize pilotního batch.
5. Dávkový překlad a export pro Substack.

---

Autor: Martin
Datum: 2026-02-08

