# Discount Culinary Institute

High-protein recipes that taste like real food. *"This doesn't taste healthy."*

Self-taught at the **Water St. campus** — the apartment where the recipes were created and
dialed in. No culinary school, no accreditation, great food.

This repo is the recipe website (the brand's ad-monetizable home), built as a static site
for GitHub Pages → eventually [discountculinary.com](https://discountculinary.com).

## Structure
```
recipes.json            ← single source of truth (29 recipes, from the Water St. cookbook)
build.py                ← generates the site from recipes.json
_source-cookbook.html   ← original cookbook UI, used as the homepage template (keep)
index.html              ← GENERATED: browsable cookbook (search + macro filters)
recipes/<slug>.html     ← GENERATED: one SEO page per recipe (JSON-LD Recipe schema)
sitemap.xml, robots.txt ← GENERATED
assets/style.css        ← recipe-page styles
assets/img/             ← drop recipe photos here as you shoot them
```

## Build
```
python3 build.py
```
Edit `recipes.json` (or add photos), re-run, commit. Never hand-edit the generated files.

## SEO notes
- Each recipe is a real static page with [Recipe structured data](https://developers.google.com/search/docs/appearance/structured-data/recipe)
  so Google can show rich results (photo, macros, ratings) — this is where recipe traffic
  comes from, **not** the brand name. Validate at search.google.com/test/rich-results.
- Add `image` fields to recipes + JSON-LD once photos exist (big rich-result boost).

## Custom domain (later)
1. Buy `discountculinary.com`.
2. Add a `CNAME` file containing `discountculinary.com` to the repo root.
3. Point DNS (A records to GitHub Pages IPs + CNAME for www) per GitHub's docs.
4. In repo Settings → Pages, set the custom domain and enable HTTPS.
5. Change `BASE_URL` in `build.py` to `https://discountculinary.com` and rebuild.
