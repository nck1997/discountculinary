#!/usr/bin/env python3
"""
Discount Culinary Institute — static site builder.

Single source of truth: recipes.json
Outputs:
  - index.html              rebranded browsable cookbook (search + macro filters)
  - recipes/<slug>.html     one SEO page per recipe, with JSON-LD Recipe schema
  - sitemap.xml, robots.txt

Run:  python3 build.py
"""
import json, html, re, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
SITE_NAME = "Discount Culinary Institute"
SLOGAN = "This doesn't taste healthy."
AUTHOR = "Nik"
# Pages URL for now; swap to https://discountculinary.com once the domain is transferred.
BASE_URL = "https://nck1997.github.io/discountculinary"
TAGLINE = ("Sneaky high-protein recipes that taste like real food. Self-taught at the "
           "Water St. campus — no formal training, no accreditation, great food.")

recipes = json.loads((ROOT / "recipes.json").read_text())
by_slug = {r["slug"]: r for r in recipes}


def esc(s):
    return html.escape(str(s), quote=True)


def per(r, key):
    return round(r.get(key, 0) / r["servings"]) if r.get("servings") else 0


# ---------------------------------------------------------------- index.html
def build_index():
    src = (ROOT / "_source-cookbook.html").read_text()

    # 1) centralize data: replace the inline RECIPES array with recipes.json
    new_array = "const RECIPES = " + json.dumps(recipes, ensure_ascii=False) + ";"
    src = re.sub(r"const RECIPES\s*=\s*\[[\s\S]*?\];", new_array, src, count=1)

    # 2) rebrand the visible strings (Water St. kept deliberately as homage)
    swaps = {
        '<div class="brand">':
            '<div class="brand"><img src="assets/crest.svg" '
            'alt="Discount Culinary Institute crest" '
            'style="display:block;width:100%;max-width:220px;margin:2px auto 12px">',
        "<title>Water St Cookbook</title>":
            f"<title>{SITE_NAME} — high-protein recipes that don't taste healthy</title>",
        '<h1>Water St Cookbook</h1>': f'<h1>{SITE_NAME}</h1>',
        '<p>A living recipe library for the meals you actually make, repeat, refine, and track.</p>':
            f'<p>{esc(SLOGAN)} High-protein recipes from the Water St. campus.</p>',
        '<div class="page-title">Water St Cookbook</div>':
            f'<div class="page-title">{SITE_NAME}</div>',
        '<h2>Cookbook, but useful</h2>':
            f'<h2>{esc(SLOGAN)}</h2>',
        ('<p>Search by dish, ingredient, or tag. Filter for higher-protein meals. Click any '
         'card for the full recipe, macros, and related dishes. Built to feel like your actual '
         'cooking rotation instead of a generic recipe dump.</p>'):
            ('<p>Comfort food that’s secretly loaded with protein. Search by dish, '
             'ingredient, or tag, and filter by protein and calories. Every recipe was created '
             'and dialed in at the Water St. campus — the apartment where the self-taught '
             '“degree” happened. No culinary school. No accreditation. Great food.</p>'
             '<p style="margin:10px 0 0;font-style:italic;color:#7a5b44">Haud Sanum Sapit '
             '— “it doesn’t taste healthy.” · Est. Water St. Campus · No accreditation, '
             'no debt, great food.</p>'),
        ('Water St Cookbook — living HTML recipe library — designed for repeat cooking, '
         'not blog SEO sludge'):
            (f'{SITE_NAME} — born at the Water St. campus — high-protein home cooking, '
             f'no formal training required'),
    }
    for a, b in swaps.items():
        if a not in src:
            print(f"  ! index swap not found: {a[:50]!r}")
        src = src.replace(a, b)

    # 3) SEO + social meta in <head>
    meta = f'''<meta name="description" content="{esc(TAGLINE)}">
<meta property="og:title" content="{esc(SITE_NAME)}">
<meta property="og:description" content="{esc(SLOGAN)} High-protein recipes that taste like real food.">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE_URL}/">
<link rel="canonical" href="{BASE_URL}/">
'''
    src = src.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                      '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + meta)

    # 4) make the in-app detail view link out to the SEO page (and let cards deep-link)
    src = src.replace(
        "<div class=\"footer-note\">",
        "<p style=\"margin:18px 0 0\"><a id=\"seoLink\" href=\"#\" target=\"_blank\" "
        "rel=\"noopener\">View / print the full recipe page →</a></p><div class=\"footer-note\">"
    )
    src = src.replace(
        "document.getElementById(\"backBtn\").addEventListener(\"click\",renderList);",
        "var _sl=document.getElementById('seoLink'); if(_sl) _sl.href='recipes/'+recipe.slug+'.html';"
        "document.getElementById(\"backBtn\").addEventListener(\"click\",renderList);"
    )

    # show recipe photos on cards + detail view when a recipe has an image
    src = src.replace(
        "<div class=\"card-media\">Water St</div>",
        "'+(recipe.image?'<div class=\"card-media\" style=\"background-image:url('+recipe.image"
        "+');background-size:cover;background-position:center\"></div>':'<div class=\"card-media\">"
        "Water St</div>')+'"
    )
    src = src.replace(
        "<div class=\"detail-media\">Recipe Detail</div>",
        "'+(recipe.image?'<div class=\"detail-media\" style=\"background-image:url('+recipe.image"
        "+');background-size:cover;background-position:center\"></div>':'<div class=\"detail-media\">"
        "Recipe Detail</div>')+'"
    )

    (ROOT / "index.html").write_text(src)
    print(f"  index.html  ({len(recipes)} recipes embedded)")


# ----------------------------------------------------- per-recipe SEO pages
RECIPE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {site}</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title} — {site}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<link rel="stylesheet" href="../assets/style.css">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<main class="recipe">
  <p class="back"><a href="../index.html">← {site}</a></p>
  <p class="kicker">{tags}</p>
  <h1>{title}</h1>
  <p class="summary">{summary}</p>
  {image_block}
  <div class="stats">
    <div><span>Servings</span><strong>{servings}</strong></div>
    <div><span>Calories / serving</span><strong>{cal_serv}</strong></div>
    <div><span>Protein / serving</span><strong>{prot_serv}g</strong></div>
    <div><span>Total</span><strong>{cal_total} kcal · {prot_total}g</strong></div>
  </div>
  <section><h2>Ingredients</h2><ul>{ingredients}</ul></section>
  <section><h2>Steps</h2><ol>{steps}</ol></section>
  {notes}
  {related}
  <p class="slogan">“{slogan}”</p>
  <footer>{site} · created at the Water St. campus · <a href="../index.html">all recipes</a></footer>
</main>
</body>
</html>
"""


def jsonld_for(r):
    data = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r["summary"],
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
        "recipeCategory": r["tags"][0] if r.get("tags") else "Main",
        "keywords": ", ".join(r.get("tags", [])),
        "recipeYield": f'{r["servings"]} servings',
        "recipeIngredient": r["ingredients"],
        "recipeInstructions": [
            {"@type": "HowToStep", "text": s} for s in r["steps"]
        ],
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


def build_recipe_pages():
    out = ROOT / "recipes"
    out.mkdir(exist_ok=True)
    for r in recipes:
        notes = (f'<section><h2>Notes</h2><p>{esc(r["notes"])}</p></section>'
                 if r.get("notes") else "")
        image_block = (f'<img class="hero-photo" src="../{r["image"]}" '
                       f'alt="{esc(r["title"])}">' if r.get("image") else "")
        rel = [by_slug[s] for s in r.get("related", []) if s in by_slug]
        related = ""
        if rel:
            links = " ".join(
                f'<a href="{s["slug"]}.html">{esc(s["title"])}</a>' for s in rel)
            related = f'<section class="related"><h2>Related</h2>{links}</section>'
        page = RECIPE_TMPL.format(
            title=esc(r["title"]), site=esc(SITE_NAME), slogan=esc(SLOGAN),
            meta_desc=esc(r["summary"][:155]),
            url=f'{BASE_URL}/recipes/{r["slug"]}.html',
            tags=" · ".join(esc(t) for t in r.get("tags", [])),
            summary=esc(r["summary"]),
            servings=r["servings"], cal_serv=per(r, "kcal_total"),
            prot_serv=per(r, "protein_total"),
            cal_total=r["kcal_total"], prot_total=r["protein_total"],
            ingredients="".join(f"<li>{esc(i)}</li>" for i in r["ingredients"]),
            steps="".join(f"<li>{esc(s)}</li>" for s in r["steps"]),
            notes=notes, related=related, image_block=image_block,
            jsonld=jsonld_for(r),
        )
        (out / f'{r["slug"]}.html').write_text(page)
    print(f"  recipes/*.html  ({len(recipes)} pages)")


# ------------------------------------------------------ sitemap + robots
def build_sitemap():
    today = datetime.date(2026, 6, 27).isoformat()
    urls = [f"{BASE_URL}/"] + [f'{BASE_URL}/recipes/{r["slug"]}.html' for r in recipes]
    body = "".join(
        f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}</urlset>\n")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    print("  sitemap.xml + robots.txt")


if __name__ == "__main__":
    print("Building Discount Culinary Institute…")
    build_index()
    build_recipe_pages()
    build_sitemap()
    print("Done.")
