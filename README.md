# Discount Culinary Institute

High-protein recipes that taste like real food. *"This doesn't taste healthy."*

Self-taught at the **Water St. campus** — the apartment where the recipes were created and
dialed in. No culinary school, no accreditation, great food.

Live: https://nck1997.github.io/discountculinary/ (GitHub Pages, served from `main`).
Eventually: [discountculinary.com](https://discountculinary.com).

## What's on the site
- **Recipes** (`index.html`) — a wall of photos held up with blue painter's tape. Search, tag
  filters, minimum protein and maximum calories per serving.
- **Recipe pages** (`recipes/<slug>.html`) — one real page per recipe for search engines
  (JSON-LD Recipe schema), tick-off ingredients, print view, and "Build a meal around this".
- **Macro Lab** (`lab/`) — the calorie slider: set calories, protein and fiber, pin what you
  already know you're eating, and it fills in the rest from these recipes, pantry staples,
  Taco Bell, Chipotle, Panda Express, CAVA and Wingstop. (Merged in from the
  `calorie-slider` repo.)

## Structure
```
recipes.json            ← single source of truth for recipes
build.py                ← generates the whole site from recipes.json
DESIGN.md               ← the rules of the look (also loaded into Raven as a taste profile)
assets/site.css         ← one stylesheet for every page
assets/home.js          ← recipe wall filtering
assets/lab.js           ← Macro Lab logic
assets/mark.svg         ← brand mark (crest.svg is the long-form crest)
assets/img/             ← recipe photos, one per slug (SOURCES.md lists the stock ones)
data/                   ← Macro Lab data; personal-recipes.js is GENERATED from recipes.json
scripts/build-taco-bell-data.js ← refreshes the Taco Bell data (node)
index.html, recipes/, lab/index.html, sitemap.xml, robots.txt ← GENERATED
_source-cookbook.html   ← the original Water St. Cookbook, kept as an archive (not used by the build)
```

## Build
```
python3 build.py
```
Edit `recipes.json` (or add photos — see `PHOTOS.md`), re-run, commit, push. Never hand-edit
the generated files.

## Design
Paper and ink, painter's-tape blue as the only accent, sticky notes only where there's a real
note. Handwriting fonts are for tape labels and sticky notes; everything you need to read
while cooking is in a plain text face. Full rules: `DESIGN.md`. Audited with
[Raven MCP](https://ravenmcp.ai) (contrast, tap targets, taste profile `discount-culinary`).

## SEO notes
- Each recipe is a static page with [Recipe structured data](https://developers.google.com/search/docs/appearance/structured-data/recipe).
  Validate at search.google.com/test/rich-results.

## Custom domain (later)
1. Buy `discountculinary.com`.
2. Add a `CNAME` file containing `discountculinary.com` to the repo root.
3. Point DNS (A records to GitHub Pages IPs + CNAME for www) per GitHub's docs.
4. In repo Settings → Pages, set the custom domain and enable HTTPS.
5. Change `BASE_URL` in `build.py` to `https://discountculinary.com` and rebuild.
