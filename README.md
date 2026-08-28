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
├── .github/workflows/
│   ├── deploy.yml          publishes to Pages on every push to main
│   └── refresh-archetype-index.yml  rebuilds the fallback index monthly
├── data/
│   └── archetype-art.js    one portrait URL per archetype, the offline fallback
├── tools/
│   ├── build-archetype-index.py     regenerates that file
│   └── index-change-report.py       says whether a rebuild is worth committing
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

For the last two, the image is fetched and inlined as a data URL so exports stay self-contained. If the host refuses cross-origin reads the portrait can only be linked: it still shows in the preview, but the row turns pink and raster export is refused rather than writing a file with a blank where the art should be — download that image and upload it as a file, or export SVG.

YGOPRODeck's image host sends no CORS headers, so its bytes can't be read directly. When a direct read is refused the image is retried through **images.weserv.nl**, and then through **i0.wp.com** if that one is unreachable — image proxies that re-serve it with the header set — that's what lets *Get all art* produce a chart you can export as PNG. A host that allows the read is never sent anywhere; the proxy is only ever a fallback, and it only ever hands back a re-encoded image. It re-compresses, so a proxied portrait is slightly smaller and slightly softer than the original — upload the file by hand if you want it untouched.

If the proxy can't reach the image either, the portrait falls back to a plain link: it still shows in the preview, but raster export is refused until you upload that one as a file.

If YGOPRODeck's lookup itself can't be reached, the archetype is resolved against `data/archetype-art.js` instead — one portrait URL per archetype, about 50 KB, picked so it matches whatever the live lookup would have returned. It only loads when the live lookup fails, so a normal visit never pays for it. The image is still fetched over the network as usual, so this covers the lookup going down, not your connection. Archetypes printed after the file was last generated won't be in it, and *Get all art* says so when it uses it. See [Refreshing the archetype index](#refreshing-the-archetype-index).

**Fetch art that blocks direct copying through a proxy** turns the fallback off. With it off, nothing but YGOPRODeck is contacted; art it won't hand over directly is linked instead of embedded, so raster export is refused while any of it is on the chart. The setting is remembered in your browser and is deliberately *not* written into **Save setup**, so loading someone else's setup never changes it for you.

Art is keyed per archetype and per sub-archetype, so a *Ryzeal* portrait and a *Fiendsmith Ryzeal* bubble are set separately. **Save setup** writes colours, portraits, settings and rows to a JSON file — reload it next event and you keep your whole art library.

### Refreshing the archetype index

`data/archetype-art.js` is a snapshot. Roughly **four new archetypes are printed a month** — about 44 a year over 2021–25 — and a tournament chart leans on recent ones, so left alone it decays exactly where it's needed.

`.github/workflows/refresh-archetype-index.yml` rebuilds it on the 1st of each month, which keeps the gap to about a set's worth. It commits only when archetypes were actually added or removed, not merely because the file was regenerated, and deploys afterwards — a push made with `GITHUB_TOKEN` can't trigger the deploy workflow on its own, so it calls it explicitly. The run summary lists what changed. You can also start it by hand from the **Actions** tab.

To rebuild locally:

```bash
python3 tools/build-archetype-index.py
python3 tools/index-change-report.py   # optional: what moved, and whether it's worth committing
```

The generator reads the card dump from YGOPRODeck, keeps one image URL per archetype, and rewrites the file — commit the result. It refuses to write if it comes back with an implausibly small number of archetypes, so a bad response can't quietly empty the fallback. Nothing else in the repository is generated, and the site still needs no build step.

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

SVG export is fully vector, with portraits embedded so the file stands on its own — except for any portrait that could only be linked, which is referenced by URL and needs a connection to show. Embedding is what makes those files big: a chart with art on every slice runs to a few megabytes of SVG, against a few hundred kilobytes of PNG. The other caveat is that raster export renders text in a system sans-serif, so it can differ very slightly from the on-screen preview.

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

**2. Turn on Pages.** Repo → **Settings** → **Pages** → **Build and deployment** → Source: **GitHub Actions**. Don't pick "Deploy from a branch" — the workflow in `.github/workflows/` handles it. There's still no build step; the workflow just uploads the repository as-is and publishes it.

**3. Set the custom domain.** Same page, **Custom domain** → `metaslice.reizu.dev` → Save. GitHub verifies the DNS, which usually takes a minute or two but can take up to an hour. Once the check passes, tick **Enforce HTTPS** (the certificate is issued automatically).

That's it. Every push to `main` republishes; you can also trigger a deploy by hand from the **Actions** tab.

### DNS

You already have the record, so this is just for reference — a subdomain needs a single `CNAME` pointing at your Pages host:

| Type | Name | Value |
| --- | --- | --- |
| CNAME | `metaslice` | `<you>.github.io` |

The value is your **user** Pages host (`<you>.github.io`), not the repo name — that's true even though the repo is called `metaslice`. The `CNAME` file in this folder holds the same domain; keep it, because a deploy without it resets the custom domain in Settings.

### Notes

- Nothing is run over the files on the way out — the workflow uploads them and Pages serves them verbatim, so there's no Jekyll pass and no need for a `.nojekyll`. The upload leaves out dot-prefixed files and always excludes `.github`, so the workflow itself isn't served. `CNAME` has no leading dot, so it ships with every deploy and the custom domain sticks.
- The social card at `assets/og-image.png` is referenced with absolute URLs in the `<head>`, since Discord, X, Slack and friends won't resolve relative ones. If you move the site to a different domain, update the `og:`/`twitter:` tags, `canonical`, `CNAME`, `sitemap.xml` and `robots.txt` — the domain appears in those five places and nowhere else.
- The `samples/` folder ships with the site so you can link people straight at an example file. Delete it if you'd rather not serve it.

## Any other host

It's all static files — Netlify, Cloudflare Pages, S3, or a folder on a NAS all work with zero changes.

Your results never leave the tab: files you load, the rows you type, colours and saved setups are all held in memory and written straight back to your own disk. Two features do reach out, both only when you ask for art:

| | |
| --- | --- |
| `db.ygoprodeck.com` | the archetype lookup behind **Get all art** and **Get card art** — it sees the archetype name |
| `images.weserv.nl` | the fallback that fetches a portrait whose host refuses a direct read — it sees the image URL, and can be switched off in **Slices** |
| `i0.wp.com` | only if weserv is unreachable — same job, same thing seen, same switch |

Neither sees your tournament results. If you'd rather nothing left the tab at all, set portraits with **Upload an image**, which never makes a request.

The offline archetype index adds no third host: it ships with the site, and the URLs in it point back at YGOPRODeck's own image host.

## Sample data

```
Placement,Player,Archetype,Sub
1,Muto B.,Tenpai Dragon,
2,Wheeler C.,White Forest,Azamina
5,Devlin F.,Ryzeal,Fiendsmith
```
