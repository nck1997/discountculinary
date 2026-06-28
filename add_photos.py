#!/usr/bin/env python3
"""
Ingest food photos into the site.

You: export the photos you want into  assets/img/incoming/  and name each file
after the recipe (e.g. "saag chicken.heic", "Mexican Cottage Pie.jpg"). HEIC is fine.
Then run:  python3 add_photos.py

It will:
  - match each photo to a recipe by (slugified) filename
  - convert + resize to a web-optimized JPG at  assets/img/<slug>.jpg  (via sips)
  - set recipes.json["image"] for matched recipes
  - rebuild the site (runs build.py)
  - report anything it couldn't match so you can rename + rerun

A photo named exactly "<slug>.jpg" always wins. Otherwise it fuzzy-matches the
filename against recipe titles and prints what it guessed.
"""
import json, re, subprocess, sys, pathlib, difflib

ROOT = pathlib.Path(__file__).parent
INCOMING = ROOT / "assets" / "img" / "incoming"
OUTDIR = ROOT / "assets" / "img"
MAXDIM = 1280  # longest edge, px
EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tiff"}

recipes = json.loads((ROOT / "recipes.json").read_text())
slugs = {r["slug"] for r in recipes}
# title (slugified) -> slug, for human filenames like "Mexican Cottage Pie"
title_to_slug = {re.sub(r"[^a-z0-9]+", "-", r["title"].lower()).strip("-"): r["slug"]
                 for r in recipes}


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def match(stem):
    s = slugify(stem)
    if s in slugs:
        return s, "exact"
    if s in title_to_slug:
        return title_to_slug[s], "title"
    # fuzzy: against slugs and title-slugs
    pool = list(slugs) + list(title_to_slug)
    hit = difflib.get_close_matches(s, pool, n=1, cutoff=0.6)
    if hit:
        return title_to_slug.get(hit[0], hit[0]), "fuzzy"
    return None, None


def convert(src, dst):
    # sips handles HEIC/PNG/TIFF/JPG natively on macOS: resize longest edge + to jpeg
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
                    "-Z", str(MAXDIM), str(src), "--out", str(dst)],
                   check=True, capture_output=True)


def main():
    INCOMING.mkdir(parents=True, exist_ok=True)
    files = [f for f in sorted(INCOMING.iterdir())
             if f.is_file() and f.suffix.lower() in EXTS]
    if not files:
        print(f"No photos in {INCOMING}. Drop labeled food photos there and rerun.")
        return
    by_slug = {r["slug"]: r for r in recipes}
    matched, unmatched, fuzzy = 0, [], []
    for f in files:
        slug, how = match(f.stem)
        if not slug:
            unmatched.append(f.name)
            continue
        dst = OUTDIR / f"{slug}.jpg"
        try:
            convert(f, dst)
        except subprocess.CalledProcessError as e:
            print(f"  ! convert failed for {f.name}: {e.stderr.decode()[:120]}")
            continue
        by_slug[slug]["image"] = f"assets/img/{slug}.jpg"
        matched += 1
        line = f"  ✓ {f.name}  ->  {slug}.jpg"
        if how == "fuzzy":
            fuzzy.append(slug)
            line += "   (FUZZY guess — verify)"
        print(line)

    (ROOT / "recipes.json").write_text(json.dumps(recipes, ensure_ascii=False, indent=2))
    print(f"\nMatched {matched}/{len(files)} photos.")
    if fuzzy:
        print(f"Fuzzy guesses to double-check: {', '.join(fuzzy)}")
    if unmatched:
        print("Could NOT match (rename to a recipe and rerun):")
        for n in unmatched:
            print(f"  - {n}")
    print("\nRebuilding site…")
    subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)
    print("Done. Commit + push when it looks right.")


if __name__ == "__main__":
    main()
