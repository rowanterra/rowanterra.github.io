# rowanterra.com

Personal website of Rowan R. Terra. Plain HTML pages written by one Python script that uses only the standard library. The built pages are kept in the repository, so the site still opens and can be edited by hand if the script is never run again.

## Layout

| Path | Contents |
|---|---|
| `content/` | Page text. `site.txt` (name, links, contact note), `about.md`, `people.md`, `publications.md`, `papers.bib`, `news/*.md`, `tools/*.md`. |
| `public/` | The built site. GitHub Pages serves a copy of this folder. |
| `public/assets/` | Stylesheet, images, CV PDF and page images, and the tool pages. Kept by hand; the build does not change them. |
| `tools/build_site.py` | Writes every page in `public/` from `content/`. |
| `tools/lint_copy.py` | Lists AI-style wording in a built page. |
| `tools/icons.json` | SVG paths of the contact icons. |
| `tests/check_site.py` | Checks local links, external loads, page structure and the sitemap. |
| `.github/workflows/deploy.yml` | On each push to `main`: build, check, publish `public/` to the `gh-pages` branch. |

## Edit and build

Text changes go in `content/`. Markdown support is a small subset: paragraphs, `##` headings, `---` rules, `*italic*`, `**bold**`, `[text](url)`, two trailing spaces for a line break, pipe tables, and lines of raw HTML.

```bash
python3 tools/build_site.py
python3 tests/check_site.py
python3 tools/lint_copy.py public/index.html
python3 -m http.server -d public 8000      # preview at http://localhost:8000
```

A file edited on github.com (phone or browser) is enough: the workflow runs the build on push. Run the build locally before a commit when the built pages in `public/` should match the content.

Common changes:

- **News item:** add `content/news/announcement_N.md` with `date: YYYY-MM-DD` in the front matter. `hidden: yes` keeps an item in the record without showing it.
- **Publication:** add a BibTeX entry to `content/papers.bib`. Site fields: `abbr` (venue tag), `preview` (cover image file in `public/assets/img/publication_preview/`), `html` (link).
- **Tool card:** add `content/tools/<name>.md` with `title`, `description`, `category` (`software` or `utilities`), `order`, `page`, `thumb`, and optional `github`. The tool page goes in `public/assets/html/`, the square thumbnail (about 770 px) in `public/assets/img/`.
- **CV:** replace the PDF in `public/assets/pdf/` (name `terra_cv_YYYY-MM-DD_web.pdf`) and the page images in `public/assets/img/cv/` (`terra_cv_YYYY-MM-DD_pN.png`, 1275 x 1650 px). The build links the newest PDF and every page image.

## Hosting

GitHub Pages, branch `gh-pages`, custom domain `rowanterra.com` (`public/CNAME`). `public/.nojekyll` stops GitHub from running Jekyll on the files. Any static host can serve `public/` unchanged.

## Credits

Contact icons are glyph outlines from Font Awesome Free 6.7.1 (CC BY 4.0) and Academicons (SIL Open Font License 1.1).

Copyright 2026 Rowan R. Terra. All rights reserved.
