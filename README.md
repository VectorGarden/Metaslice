# Metaslice

*Top cut, sliced.*

Turn tournament results into a shareable archetype pie chart — the kind of breakdown YGOPRODeck publishes after a YCS — and export it as PNG, JPG, WEBP, AVIF or SVG.

Everything runs in the browser. No build step, no server, no dependencies to install: open `index.html` and go.

Live at **[metaslice.reizu.dev](https://metaslice.reizu.dev/)**.

```
metaslice/
├── index.html              the whole app
├── 404.html                themed not-found page
├── CNAME                   custom domain for GitHub Pages
├── site.webmanifest        installable-app metadata
├── robots.txt
├── sitemap.xml
├── LICENSE                 MIT
├── assets/
│   ├── icon.svg            source icon (also the in-app logo)
│   ├── favicon.ico         multi-size 16→256 for hosting
│   ├── icon-256.png
│   ├── icon-512.png
│   ├── card-back.png       the default face of the Other slice (also inlined)
│   └── og-image.png        1200×630 social preview card
└── samples/
    ├── ycs-top-cut.csv     one row per deck, with placements
    ├── regional-summary.tsv  pre-counted totals
    └── meta-share.json
```

## Getting results in

Three ways, all in the **Results** panel: drop a file, paste rows, or type them into the table. There's also a sample event if you just want to see the thing work.

Columns are matched by name, in any order, case-insensitively. Anything unrecognised is ignored.

| Column | Also accepts | What it does |
| --- | --- | --- |
| `archetype` | deck, deck name, theme, strategy, name | The slice. Required. |
| `sub` | sub-archetype, variant, engine, package, build | Splits a slice into bubbles. Optional. |
| `count` | entries, decks, qty, players, total, # | How many decks. Leave it out and each row counts as one. |
| `placement` | place, rank, finish, standing | Enables the top-cut filter. |
| `image` | img, art, url | Portrait for that archetype, filled in automatically. |

Both shapes work: **one row per deck** (with a placement) or **one row per archetype** (with a count). JSON can be an array of objects, an array of arrays, or a plain `{"Ryzeal": 13, "Maliss": 6}` map. XLSX is read with SheetJS, pulled from a CDN the first time you open a spreadsheet — offline, save as CSV instead.

## Archetype art

**Get all art** is the fast path: one click walks every archetype and sub-archetype on the chart, looks each one up on YGOPRODeck, and fills in whatever it finds — roughly a second per ten entries. Anything without a match is listed at the end so you can fill those few by hand. It only fills gaps, so art you've already set is never overwritten. **Clear all art** wipes the lot.

Or click any portrait in the **Slices** panel to set that one on its own. Three options:

- **Upload an image** — always works, always exports.
- **Get card art from YGOPRODeck** — looks up the archetype and grabs the cropped card art.
- **Paste an image URL** — anything on the web.

For the last two, the image is fetched and inlined as a data URL so exports stay self-contained. If the host refuses cross-origin reads, the portrait still shows in the preview but the row turns pink and raster export will be blocked — download that image and upload it as a file, or export SVG.

Art is keyed per archetype and per sub-archetype, so a *Ryzeal* portrait and a *Fiendsmith Ryzeal* bubble are set separately. **Save setup** writes colours, portraits, settings and rows to a JSON file — reload it next event and you keep your whole art library.

## Chart controls

- **Top cut** — 4 / 8 / 16 / 32 / 64. Uses the placement column when there is one; otherwise it keeps the N most-played archetypes and says so.
- **Other threshold** — anything under the slider (default 5%, 0 turns it off) folds into a grey *Other* slice. Its members survive as sub-bubbles, shaded bands and legend entries. A one-archetype *Other* is never created. *Other* ships with a card back as its face — that artwork is original to this project, not Konami's; click its portrait to swap in whatever you prefer, or Reset to bring it back.
- **Art fills the whole slice** — a toggle under the art switch. Instead of a circular portrait, the archetype's image is clipped to the wedge itself, centred on the wedge's own bounding box, tinted with the slice colour so the palette still reads and labels stay legible. Archetypes without art keep their plain slice.
- **Sub-archetype bubbles** — small circular portraits near the rim, one per variant. Each variant also gets its own shaded band across the wedge with a divider between them, so you can read how the slice splits — at low contrast on a flat slice, stronger over artwork, and always drawn above the art so filling the slice never hides the breakdown. Hover any band for the exact split.
- Labels around the edge with collision-avoided leader lines, inside the slices, or legend-only. Legend right, underneath, or off.
- Centre hole for a donut (the total sits in the middle), slice gap, deck counts next to percentages, alphabetical order.
- Light/dark toggle in the header — the chart follows it, so exports match what you see, and your choice is remembered next visit.

## Export

**What goes in the file** picks how much of the chart gets exported, and the preview follows your choice so it's always what you'll get:

| | Contents | Canvas |
| --- | --- | --- |
| **Pie only** | Slices, art and sub-bubbles. Nothing else. | Square, tight crop — good for thumbnails and stream overlays |
| **Pie + labels** | Adds the names and percentages, no legend | Wide |
| **Everything** | Title, subtitle, labels and legend | Wide |

PNG, JPG, WEBP, AVIF, or SVG. Set any width from 200 to 8000 px; height follows the chart's aspect ratio. Transparent background is available for everything except JPG. **Copy image** puts a PNG straight on the clipboard.

AVIF and WEBP encoding depends on the browser. If yours can't write the format you picked, the file is saved as the next best one and a note tells you which.

SVG export is fully vector and self-contained, with portraits embedded — the one caveat is that raster export renders text in a system sans-serif, so it can differ very slightly from the on-screen preview.

## Icon

The tab icon is inlined into `index.html` as a base64 SVG, so it shows up from `file://` and from any folder without needing the assets to resolve. `assets/` holds the same artwork as separate files for hosting — `icon.svg`, a multi-size `favicon.ico` (16–256px), and 256/512px PNGs for touch icons. If you edit `icon.svg`, re-inline it with:

```bash
python3 -c "import base64;print(base64.b64encode(open('assets/icon.svg','rb').read()).decode())"
```

## Publishing to GitHub Pages

This repo is already wired for it — there's no build step, so the repository *is* the site. One-time setup:

**1. Push it up.** From inside this folder:

```bash
git init -b main
git add .
git commit -m "Metaslice"
git remote add origin git@github.com:<you>/metaslice.git
git push -u origin main
```

**2. Turn on Pages.** Repo → **Settings** → **Pages** → **Build and deployment** → Source: **Deploy from a branch**, branch `main`, folder `/ (root)`. There's no build step, so GitHub serves the files as they are — nothing else to configure.

**3. Set the custom domain.** Same page, **Custom domain** → `metaslice.reizu.dev` → Save. GitHub verifies the DNS, which usually takes a minute or two but can take up to an hour. Once the check passes, tick **Enforce HTTPS** (the certificate is issued automatically).

That's it. Every push to `main` republishes.

### DNS

You already have the record, so this is just for reference — a subdomain needs a single `CNAME` pointing at your Pages host:

| Type | Name | Value |
| --- | --- | --- |
| CNAME | `metaslice` | `<you>.github.io` |

The value is your **user** Pages host (`<you>.github.io`), not the repo name — that's true even though the repo is called `metaslice`. The `CNAME` file in this folder holds the same domain; keep it, because a deploy without it resets the custom domain in Settings.

### Notes

- Pages runs the files through Jekyll on the way out. That's harmless here: nothing is named with a leading underscore, and neither `index.html` nor `404.html` contains Liquid syntax for it to touch. A `.nojekyll` file would skip the pass, but there's nothing for it to protect.
- The social card at `assets/og-image.png` is referenced with absolute URLs in the `<head>`, since Discord, X, Slack and friends won't resolve relative ones. If you move the site to a different domain, update the `og:`/`twitter:` tags, `canonical`, `CNAME`, `sitemap.xml` and `robots.txt` — the domain appears in those five places and nowhere else.
- The `samples/` folder ships with the site so you can link people straight at an example file. Delete it if you'd rather not serve it.

## Any other host

It's all static files — Netlify, Cloudflare Pages, S3, or a folder on a NAS all work with zero changes. Nothing is uploaded anywhere at runtime: results, art and setups stay in the tab.

## Sample data

```
Placement,Player,Archetype,Sub
1,Muto B.,Tenpai Dragon,
2,Wheeler C.,White Forest,Azamina
5,Devlin F.,Ryzeal,Fiendsmith
```
