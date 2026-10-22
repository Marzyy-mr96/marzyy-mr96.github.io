# Marzieh Allahyari — personal research website

A fast, static, accessible academic site. Content lives in plain text files; one command rebuilds every page.

## Folder layout

```
website/
├── content/
│   ├── site.json            ← name, intro, about, education, teaching, skills, links, highlights
│   ├── publications.json    ← publications by status (Published / Accepted / Under review / …)
│   └── projects/*.md        ← one file per project (each becomes a page + a card)
├── assets/                  ← css, js (main.js, demo.js), img (portrait, favicon)
├── files/                   ← downloadable files (CV PDF)
├── build.py                 ← generator (Python 3.7+, no extra packages)
└── docs/                    ← GENERATED site — do not edit by hand
```

## Common updates

**Rebuild after any change:** `python build.py`

| I want to… | Edit |
|---|---|
| Add a publication / change its status | Move or add an item in `content/publications.json`. Empty sections are hidden automatically. |
| Add a project | Copy any `content/projects/*.md`, change the front matter (title, category, summary, status, order, featured, tools) and the text. The file name becomes the URL. A new `category` automatically gets its own filter button. |
| Feature a project on the home page | Set `featured: yes` in that project's front matter. |
| Update the CV | Replace `files/Marzieh_Allahyari_CV.pdf` (keep the name). |
| Change intro, highlights, skills, teaching | `content/site.json` |
| Change the photo | Replace `assets/img/portrait.jpg` (about 640 × 768 px). |

**Markdown supported in project files:** `## Heading`, paragraphs, `- bullet`, `**bold**`, `*italic*`, `[text](https://…)`. Internal links are written from the site root (e.g. `[demo](projects/uncertainty-demo.html)`). Put `{{demo}}` on its own line to insert the interactive demo.

## Preview locally

```bash
python -m http.server 8765 --directory docs
```
Then open http://localhost:8765

## Deploy to GitHub Pages (free) — only after you approve the content

1. Create a GitHub account (if needed) and a **new public repository**, e.g. `marzieh-allahyari.github.io` (this name gives the URL `https://<username>.github.io`).
2. In `content/site.json`, set `"site_url"` to that URL and run `python build.py` (this fixes canonical links and the sitemap).
3. Upload this `website` folder to the repository (GitHub Desktop is the easiest way: *Add existing repository → Publish*).
4. On GitHub: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs`** → Save.
5. After a minute or two the site is live. To update it later: edit content → `python build.py` → commit and push.

Alternative hosts that serve the `docs/` folder as-is: Netlify or Vercel (drag-and-drop the `docs` folder), or KU personal web space.

**Before pushing, check:** only `docs/`, `content/`, `assets/`, `files/`, `build.py`, `README.md` are in the repository; no research data, manuscripts, or survey files.

## Confidentiality rules built into this site

- Lumberton: only the public NIST SP 1230 reports are cited (as study background, not as own publications). No data, results, figures, methods-in-progress, or project ideas.
- PLOS ONE manuscript: title only (until published).
- The demo uses a textbook cantilever example, not thesis models or results.
