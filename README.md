# rowanterra.com

Personal website of Rowan R. Terra. Built with Jekyll on the [al-folio](https://github.com/alshedivat/al-folio) theme (MIT license, see `LICENSE`) and served by GitHub Pages at https://rowanterra.com.

## Pages

| Page | Source |
|---|---|
| about | `_pages/about.md`, news items in `_news/` |
| publications | `_pages/publications.md`, entries in `_bibliography/papers.bib` |
| tools | `_pages/projects.md`, entries in `_projects/` |
| cv | `_pages/cv.md`, PDF in `assets/pdf/` |
| people | `_pages/profiles.md` |

## Look

Colors, type and the top bar follow https://terracognita.earth. The colors are set in `_sass/_variables.scss` and the styles in `_sass/_terra.scss`.

## Build and deploy

A push to `main` runs `.github/workflows/deploy.yml`, which builds the site into the `gh-pages` branch. Local build:

```bash
bundle install
bundle exec jekyll serve
```
