#!/usr/bin/env python3
"""
DICE (Domestic Institute of Culinary Education) — static site builder.

Single source of truth: recipes.json
Outputs (all GENERATED — never hand-edit):
  - index.html                 photo wall: search, tag + macro filters
  - recipes/<slug>.html        one page per recipe, with JSON-LD Recipe schema
  - lab/index.html             Macro Lab (the calorie slider)
  - data/personal-recipes.js   recipes.json exposed to the Macro Lab
  - sitemap.xml, robots.txt

Look and feel: assets/site.css, rules in DESIGN.md.
Run:  python3 build.py
"""
import json, html, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
SITE_NAME = "DICE"
FULL_NAME = "Domestic Institute of Culinary Education"
AUTHOR = "Nik"
# Pages URL for now; swap to https://discountculinary.com once the domain is transferred.
BASE_URL = "https://nck1997.github.io/discountculinary"
TAGLINE = ("High-protein recipes from a self-taught home cook. Calories and protein "
           "per serving on every recipe.")
FONTS = ("https://fonts.googleapis.com/css2?family=Kalam:wght@400;700"
         "&family=Libre+Franklin:wght@400;600;700&family=Permanent+Marker&display=swap")

recipes = json.loads((ROOT / "recipes.json").read_text())
by_slug = {r["slug"]: r for r in recipes}


def esc(s):
    return html.escape(str(s), quote=True)


def per(r, key):
    return round(r.get(key, 0) / r["servings"]) if r.get("servings") else 0


# ------------------------------------------------------------------ shared
def page(*, title, desc, url, root, current, body, head_extra="", scripts=""):
    """Wrap a page body in the shared shell. `root` is '' or '../'."""
    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{root}{href}"{cur}>{label}</a>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<link rel="icon" href="{root}assets/mark.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}assets/site.css">
{head_extra}</head>
<body>
<div class="wrap">
<header class="masthead">
  <a class="brand" href="{root}index.html">
    <img src="{root}assets/mark.svg" alt="" width="56" height="56">
    <span class="brand-name">{esc(SITE_NAME)}<span class="brand-sub">{esc(FULL_NAME)}</span></span>
  </a>
  <nav class="nav" aria-label="Main">
    {nav("index.html", "Recipes", "recipes")}
    {nav("lab/index.html", "Macro Lab", "lab")}
  </nav>
</header>
{body}
<footer class="footer">
  <p>{esc(SITE_NAME)} · {esc(FULL_NAME)} · recipes by {esc(AUTHOR)}, self-taught.</p>
  <p>Calories and protein are home-kitchen estimates, per serving unless it says otherwise.</p>
  <p><a href="{root}index.html">All recipes</a> · <a href="{root}lab/index.html">Macro Lab</a></p>
</footer>
</div>
{scripts}</body>
</html>
"""


def tape(text, tag="span", extra=""):
    return f'<div class="tape-wrap{extra}"><{tag} class="tape">{esc(text)}</{tag}></div>'


def card(r, root, heading="h2"):
    img = (f'<img src="{root}{r["image"]}" alt="" loading="lazy" width="1280" height="853">'
           if r.get("image") else "")
    search = " ".join([r["title"], r["summary"], *r.get("tags", []), *r["ingredients"],
                       *r["steps"], r.get("notes", "")]).lower()
    return f"""<li class="card" data-tags="{esc('|'.join(r.get('tags', [])))}" data-protein="{per(r, 'protein_total')}" data-kcal="{per(r, 'kcal_total')}" data-search="{esc(search)}">
  <a href="{root}recipes/{r['slug']}.html">
    <div class="print">{img}</div>
    {tape(r['title'], heading)}
    <p class="card-meta"><strong>{per(r, 'kcal_total')}</strong> kcal · <strong>{per(r, 'protein_total')}g</strong> protein per serving</p>
    <p class="card-tags">{esc(' · '.join(r.get('tags', [])))}</p>
  </a>
</li>"""


# ---------------------------------------------------------------- index.html
def build_index():
    ordered = sorted(recipes, key=lambda r: r["title"].lower())
    tags = sorted({t for r in recipes for t in r.get("tags", [])}, key=str.lower)
    max_kcal = 1200
    max_protein = 80
    tag_buttons = "".join(
        f'<button type="button" class="mark-toggle" aria-pressed="false" data-tag="{esc(t)}">{esc(t)}</button>'
        for t in tags)
    body = f"""<main>
<section class="intro">
  <div class="note">
    <p class="note-big">Recipes and macros :)</p>
  </div>
  <div class="intro-copy">
    <p><a class="btn small" href="lab/index.html">Open the Macro Lab</a></p>
  </div>
</section>

<details class="filters" id="filters" open>
  <summary class="btn">Search and filters</summary>
  <div class="sheet ruled">
    <div class="filter-grid">
      <div>
        <label class="field-label" for="search">Search recipes</label>
        <input class="text-input" id="search" type="search" placeholder="Dish, ingredient, or tag" autocomplete="off">
      </div>
      <div>
        <div class="range-head">
          <label class="field-label" for="proteinRange">Protein per serving, at least</label>
          <span class="range-value"><span id="proteinValue">0</span>g</span>
        </div>
        <input id="proteinRange" type="range" min="0" max="{max_protein}" step="5" value="0">
      </div>
      <div>
        <div class="range-head">
          <label class="field-label" for="calorieRange">Calories per serving, at most</label>
          <span class="range-value"><span id="calorieValue">{max_kcal}</span></span>
        </div>
        <input id="calorieRange" type="range" min="100" max="{max_kcal}" step="25" value="{max_kcal}">
      </div>
    </div>
    <div class="tag-row" role="group" aria-label="Filter by tag">{tag_buttons}</div>
  </div>
</details>

<div class="results-bar">
  <p class="results-count" id="resultsCount" aria-live="polite">{len(recipes)} recipes</p>
  <button type="button" class="btn small" id="clearFilters" hidden>Clear filters</button>
</div>

<ul class="wall" id="wall">
{chr(10).join(card(r, "") for r in ordered)}
</ul>
<div class="empty" id="empty" hidden>
  <div class="note pink">
    <span class="note-title">Nothing matches</span>
    <p>Drop a tag, lower the protein, or raise the calories.</p>
  </div>
</div>
</main>
"""
    out = page(title=f"{SITE_NAME} — {FULL_NAME} · high-protein recipes",
               desc=TAGLINE, url=f"{BASE_URL}/", root="", current="recipes", body=body,
               head_extra='<meta property="og:type" content="website">\n',
               scripts='<script src="assets/home.js"></script>\n')
    (ROOT / "index.html").write_text(out)
    print(f"  index.html  ({len(recipes)} recipes)")


# ----------------------------------------------------- per-recipe pages
def jsonld_for(r):
    data = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r["summary"],
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Organization", "name": f"{SITE_NAME} ({FULL_NAME})"},
        "recipeCategory": r["tags"][0] if r.get("tags") else "Main",
        "keywords": ", ".join(r.get("tags", [])),
        "recipeYield": f'{r["servings"]} servings',
        "recipeIngredient": [i for i in r["ingredients"] if not i.startswith("---")],
        "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in r["steps"]],
        "nutrition": {
            "@type": "NutritionInformation",
            "calories": f'{per(r, "kcal_total")} calories',
            "proteinContent": f'{per(r, "protein_total")} g',
        },
        "url": f'{BASE_URL}/recipes/{r["slug"]}.html',
    }
    if r.get("image"):
        data["image"] = f'{BASE_URL}/{r["image"]}'
    return json.dumps(data, ensure_ascii=False, indent=2)


def ingredient_items(r):
    out = []
    for n, item in enumerate(r["ingredients"]):
        if item.startswith("---"):
            out.append(f'<li class="group">{esc(item.strip("- ").title())}</li>')
        else:
            out.append(f'<li><label><input type="checkbox" id="ing{n}"><span>{esc(item)}</span></label></li>')
    return "\n".join(out)


def build_recipe_pages():
    out = ROOT / "recipes"
    out.mkdir(exist_ok=True)
    for r in recipes:
        wip = "Work In Progress" in r.get("tags", [])
        hero = (f'<div class="hero-print"><span class="scrap tl"></span>'
                f'<img src="../{r["image"]}" alt="{esc(r["title"])}" width="1280" height="853">'
                f'<span class="scrap br"></span></div>' if r.get("image") else "")
        notes = (f'<div class="note pink"><span class="note-title">Cook\'s notes</span>'
                 f'<p>{esc(r["notes"])}</p></div>' if r.get("notes") else "")
        wip_note = ('<div class="note orange"><span class="note-title">Work in progress</span>'
                    '<p>Still dialing this one in. Cook it, but read the notes first.</p></div>'
                    if wip else "")
        rel = [by_slug[s] for s in r.get("related", []) if s in by_slug]
        related = (f'<section class="related"><h2 class="section-title">Goes with</h2>'
                   f'<ul class="wall">{"".join(card(s, "../", "h3") for s in rel)}</ul></section>'
                   if rel else "")
        s = "" if r["servings"] == 1 else "s"
        body = f"""<main>
<p class="crumbs"><a href="../index.html">← All recipes</a></p>
<div class="page-title">{tape(r['title'], 'h1', ' flat')}</div>
<p class="summary">{esc(r['summary'])}</p>
<p class="kicker">{esc(' · '.join(r.get('tags', [])))}</p>

<div class="recipe-top">
  {hero}
  <div class="side-notes">
    <div class="note">
      <span class="note-title">Per serving</span>
      <div class="note-row">
        <p><span class="note-big">{per(r, 'kcal_total')}</span>kcal</p>
        <p><span class="note-big">{per(r, 'protein_total')}g</span>protein</p>
      </div>
      <p>Makes {r['servings']} serving{s}. Whole batch: {r['kcal_total']} kcal, {r['protein_total']}g protein.</p>
    </div>
    {wip_note}
    <div class="actions">
      <a class="btn primary" href="../lab/index.html?pin={r['slug']}">Build a meal around this</a>
      <button class="btn" type="button" onclick="window.print()">Print</button>
    </div>
  </div>
</div>

<div class="recipe-body">
  <section class="sheet ruled" aria-labelledby="ing-h">
    <h2 class="section-title" id="ing-h">Ingredients</h2>
    <ul class="ingredients">
{ingredient_items(r)}
    </ul>
  </section>
  <div>
    <section aria-labelledby="steps-h">
      <h2 class="section-title" id="steps-h">Steps</h2>
      <ol class="steps">
        {"".join(f"<li>{esc(step)}</li>" for step in r["steps"])}
      </ol>
    </section>
    {notes}
  </div>
</div>
{related}
</main>
"""
        head = ('<meta property="og:type" content="article">\n'
                + (f'<meta property="og:image" content="{BASE_URL}/{r["image"]}">\n' if r.get("image") else "")
                + f'<script type="application/ld+json">\n{jsonld_for(r)}\n</script>\n')
        (out / f'{r["slug"]}.html').write_text(page(
            title=f'{r["title"]} — {SITE_NAME}', desc=r["summary"][:155],
            url=f'{BASE_URL}/recipes/{r["slug"]}.html', root="../", current="",
            body=body, head_extra=head))
    print(f"  recipes/*.html  ({len(recipes)} pages)")


# ------------------------------------------------------------- macro lab
def build_lab():
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "personal-recipes.js").write_text(
        "// GENERATED by build.py from recipes.json\nwindow.PERSONAL_RECIPES = "
        + json.dumps(recipes, ensure_ascii=False, indent=2) + ";\n")
    body = f"""<main class="lab">
<div class="page-title">{tape('Macro Lab', 'h1', ' flat')}</div>
<div class="lab-intro">
  <div>
    <p class="summary">Set calories, protein and fiber. See what fits: these recipes, a few pantry staples, and fast food for the days it comes to that.</p>
    <p class="section-note">Pin anything you already know you're eating and the lab fills in the rest.</p>
  </div>
  <div class="note green">
    <span class="note-title">On file</span>
    <div class="hero-stats" id="heroStats"></div>
  </div>
</div>

<section aria-labelledby="targets-h">
  <div class="section-heading">
    <div><p class="eyebrow">Targets</p><h2 id="targets-h">Dial in the day</h2></div>
    <p class="section-note">Slide, or type an exact number.</p>
  </div>
  <div class="slider-grid" id="sliderGrid"></div>
  <div class="filter-row">
    <div>
      <div class="filter-label">Sources</div>
      <div class="chip-group" id="sourceChips"></div>
    </div>
    <div>
      <div class="filter-label">Availability</div>
      <div class="chip-group" id="availabilityChips"></div>
    </div>
    <label class="search-box">
      <span>Search items</span>
      <input class="text-input" id="searchInput" type="search" placeholder="Chicken bowl, wings, yogurt">
    </label>
  </div>
</section>

<section id="selectionSection" aria-labelledby="pinned-h">
  <div class="section-heading">
    <div><p class="eyebrow">Pinned picks</p><h2 id="pinned-h">Lock in what you want</h2></div>
    <p class="section-note">Pin an item, set the count, and roll again to fill the rest.</p>
  </div>
  <div id="selectionSummary"></div>
  <div class="selection-grid" id="pinnedGrid"></div>
</section>

<div class="compact-pinned-bar" id="compactPinnedBar" aria-live="polite"></div>

<section id="comboResults" aria-labelledby="combo-h">
  <div class="section-heading">
    <div><p class="eyebrow">Best combos</p><h2 id="combo-h">Meals that hit the numbers</h2></div>
    <p class="section-note" id="comboSummary"></p>
  </div>
  <div class="combo-grid" id="comboGrid"></div>
</section>

<section id="itemResults" aria-labelledby="items-h">
  <div class="section-heading">
    <div><p class="eyebrow">Food library</p><h2 id="items-h">Single items in range</h2></div>
    <p class="section-note">Pin from here when you already know one piece of the meal.</p>
  </div>
  <div class="library-grid" id="itemGrid"></div>
</section>

<section id="cuisineResults" aria-labelledby="cuisine-h">
  <div class="section-heading">
    <div><p class="eyebrow">By cuisine</p><h2 id="cuisine-h">Browse by food lane</h2></div>
    <p class="section-note">The same active sources, grouped.</p>
  </div>
  <div class="cuisine-grid" id="cuisineGrid"></div>
</section>

<section id="dealResults" aria-labelledby="deals-h">
  <div class="section-heading">
    <div><p class="eyebrow">Official deals</p><h2 id="deals-h">Taco Bell boxes and combos</h2></div>
    <p class="section-note" id="dealSummary"></p>
  </div>
  <div class="deal-grid" id="dealGrid"></div>
</section>

<p class="section-note">Taco Bell nutrition comes from official Taco Bell menu pages and linked Nutritionix labels. Fast-casual numbers use official nutrition guides and common builds. Recipe and staple macros are my own. Recipes don't track fiber yet, so they count as 0g.</p>
</main>

<div class="recipe-modal hidden" id="recipeModal" role="dialog" aria-modal="true" aria-labelledby="recipeModalTitle">
  <div class="recipe-modal-backdrop" data-close-recipe="true"></div>
  <article class="recipe-panel">
    <button class="btn small recipe-close" type="button" data-close-recipe="true">Close</button>
    <div id="recipeModalContent"></div>
  </article>
</div>
"""
    scripts = ('<script src="../data/taco-bell-items.js"></script>\n'
               '<script src="../data/fast-casual-items.js"></script>\n'
               '<script src="../data/personal-recipes.js"></script>\n'
               '<script src="../assets/lab.js"></script>\n')
    (ROOT / "lab").mkdir(exist_ok=True)
    (ROOT / "lab" / "index.html").write_text(page(
        title=f"Macro Lab — {SITE_NAME}",
        desc="Set calorie, protein and fiber targets and see which recipes, staples and fast-food orders fit.",
        url=f"{BASE_URL}/lab/", root="../", current="lab", body=body,
        head_extra='<meta property="og:type" content="website">\n', scripts=scripts))
    print("  lab/index.html + data/personal-recipes.js")


# ------------------------------------------------------ sitemap + robots
def build_sitemap():
    today = datetime.date.today().isoformat()
    urls = ([f"{BASE_URL}/", f"{BASE_URL}/lab/"]
            + [f'{BASE_URL}/recipes/{r["slug"]}.html' for r in recipes])
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}</urlset>\n")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    print("  sitemap.xml + robots.txt")


if __name__ == "__main__":
    print("Building DICE…")
    build_index()
    build_recipe_pages()
    build_lab()
    build_sitemap()
    print("Done.")
