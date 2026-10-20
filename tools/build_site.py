"""Build rowanterra.com from the files in content/.

Input:  content/site.txt         site settings, one "key: value" per line
        content/about.md         home page text (front matter: title, subtitle)
        content/people.md        people page (Markdown with HTML blocks)
        content/publications.md  text above the publication list
        content/papers.bib       publications (BibTeX)
        content/news/*.md        news items (front matter: date YYYY-MM-DD, optional "hidden: yes")
        content/tools/*.md       tool cards (front matter only)
        tools/icons.json         SVG paths for the contact icons
Output: public/*.html, public/<page>/index.html, sitemap.xml, robots.txt, .nojekyll.
        Images, the stylesheet, the CV PDF and the tool pages are kept in public/assets by hand;
        the build does not change them.
Run:    python3 tools/build_site.py            (Python 3.8 or newer, standard library only)
Preview: python3 -m http.server -d public 8000, then open http://localhost:8000

Markdown support is a small subset: paragraphs, ## and ### headings, --- rules, *italic*, **bold**,
[text](url), two trailing spaces for a line break, pipe tables, and lines of raw HTML.
"""
import datetime
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT, PUBLIC = ROOT / "content", ROOT / "public"
NAV = [("about", "/"), ("publications", "/publications/"), ("tools", "/tools/"), ("cv", "/cv/"), ("people", "/people/")]


# ---------------------------------------------------------------- reading content
def read_settings(path: Path) -> dict:
    """Parse "key: value" lines; '#' lines are notes."""
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def read_page(path: Path) -> tuple:
    """Split a content file into (front-matter dict, body text). A '#' after a value starts a note."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = re.sub(r"\s+#.*$", "", v).strip()
    return meta, m.group(2)


# ---------------------------------------------------------------- Markdown subset
def inline(s: str) -> str:
    """Bold, italic, links and line breaks. Raw HTML passes through unchanged."""
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)
    s = re.sub(r" {2,}\n", "<br>\n", s)
    return s


def table(lines: list) -> str:
    """Pipe table with a header row and a --- separator row."""
    cells = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    head, rows = cells[0], cells[2:]
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>\n" for r in rows)
    return f'<div class="scroll"><table>\n<thead><tr>{th}</tr></thead>\n<tbody>\n{tb}</tbody></table></div>'


def markdown(text: str) -> str:
    """Convert the Markdown subset described in the module notes."""
    out, para, lines = [], [], text.strip("\n").split("\n")

    def flush():
        if para:
            out.append("<p>" + inline("\n".join(para)).strip() + "</p>")
            para.clear()

    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            flush()
        elif ln.strip() == "---":
            flush(); out.append("<hr>")
        elif m := re.match(r"(#{2,3}) (.*)", ln):
            flush(); n = len(m.group(1)); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"\s*\|[-| :]+\|\s*$", lines[i + 1]):
            flush()
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            out.append(table(lines[i:j])); i = j; continue
        elif ln.lstrip().startswith("<") and not para:
            out.append(ln)
        else:
            para.append(ln)
        i += 1
    flush()
    return "\n".join(out)


# ---------------------------------------------------------------- BibTeX
def parse_bib(text: str) -> list:
    """Read @Type{key, field = {value}, ...} entries. Values may contain nested braces."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", text):
        i, depth, fields = m.end(), 1, {}
        body_start = i
        while depth and i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[body_start:i - 1]
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            j = fm.end()
            if body[j] == "{":
                d, k = 1, j + 1
                while d:
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                val = body[j + 1:k - 1]
            else:
                val = re.match(r"[^,\n]*", body[j:]).group(0)
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", val).strip()
        entries.append({"type": m.group(1).lower(), "key": m.group(2).strip(), **fields})
    return entries


def authors(field: str) -> str:
    """'Last, First and Last, First' to 'First Last and First Last' (Oxford comma for three or more)."""
    names = []
    for a in field.split(" and "):
        last, _, first = a.partition(",")
        names.append(f"{first.strip()} {last.strip()}".strip())
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


BIB_SHOW = ["title", "author", "journal", "booktitle", "volume", "number", "pages", "year", "publisher", "doi"]


def bibtex(e: dict) -> str:
    """BibTeX text for the BIB button, with the site-only fields left out."""
    rows = [f"  {k:<10} = {{{e[k]}}}" for k in BIB_SHOW if k in e]
    return f"@{e['type'].capitalize()}{{{e['key']},\n" + ",\n".join(rows) + "\n}"


def publications_html(entries: list) -> str:
    """Year headings, newest first; file order within a year."""
    out = []
    years = sorted({e.get("year", "") for e in entries}, reverse=True)
    for y in years:
        out.append(f'<h2 class="year">{y}</h2>')
        for e in [e for e in entries if e.get("year", "") == y]:
            cover = ""
            if e.get("preview"):
                cover = f'<img class="cover" src="/assets/img/publication_preview/{e["preview"]}" alt="{html.escape(e.get("journal", ""))} cover" loading="lazy">'
            abbr = f'<span class="abbr">{html.escape(e["abbr"])}</span>' if e.get("abbr") else ""
            venue = e.get("journal") or e.get("booktitle", "")
            links = f'<button type="button" class="bib-btn">Bib</button>'
            if e.get("html"):
                links += f'<a href="{html.escape(e["html"])}">HTML</a>'
            au = f'<div>{html.escape(authors(e["author"]))}</div>' if e.get("author") else ""
            out.append(
                f'<div class="pub"><div>{abbr}{cover}</div><div>'
                f'<div class="title">{html.escape(e.get("title", ""))}</div>{au}'
                f'<div><span class="venue">{html.escape(venue)}</span>, {y}</div>'
                f'<div class="links">{links}</div><pre hidden>{html.escape(bibtex(e))}</pre></div></div>')
    return "\n".join(out)


# ---------------------------------------------------------------- page frame
JS_MENU = ("<script>document.querySelector('.menu-btn').onclick=function(){var n=document.querySelector('.nav');"
           "var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)};</script>")
JS_PUBS = ("<script>(function(){var f=document.querySelector('.filter');document.querySelectorAll('.bib-btn').forEach(function(b){"
           "b.onclick=function(){var p=b.closest('.pub').querySelector('pre');p.hidden=!p.hidden}});"
           "f.oninput=function(){var q=f.value.toLowerCase();document.querySelectorAll('.year').forEach(function(h){var n=h.nextElementSibling,any=false;"
           "while(n&&n.classList.contains('pub')){var s=n.textContent.toLowerCase().indexOf(q)>-1;n.hidden=!s;any=any||s;n=n.nextElementSibling}"
           "h.hidden=!any})}})();</script>")


def frame(site: dict, title: str, body: str, path: str, today: str, script: str = "", brand: bool = True) -> str:
    """Full HTML document: head, top bar, main, footer."""
    full = site["name"] if title == "about" else f"{site['name']} | {title}"
    nav = "".join(
        f'<li><a href="{href}"' + (' aria-current="page"' if href == path else "") + f">{label}</a></li>"
        for label, href in NAV)
    nav += f'<li class="tc"><a href="{site["consulting_url"]}">Terra Cognita</a></li>'
    brand_html = f'<a class="brand" href="/">{site["name"]}</a>' if brand else '<span class="brand"></span>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(site['description'])}">
<meta name="keywords" content="{html.escape(site['keywords'])}">
<meta name="author" content="{html.escape(site['name'])}">
<link rel="canonical" href="{site['url']}{path}">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{html.escape(site['description'])}">
<meta property="og:url" content="{site['url']}{path}">
<meta property="og:image" content="{site['url']}/assets/img/prof_pic.jpg">
<link rel="icon" href="/assets/img/favicon.ico">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<header class="bar"><div class="wrap">{brand_html}
<button class="menu-btn" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
<ul class="nav">{nav}</ul></div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">&copy; Copyright {today[:4]} {site['name']}. Last updated: {long_date(today)}.</div></footer>
{JS_MENU}{script}
</body>
</html>
"""


def long_date(iso: str) -> str:
    """2026-10-20 to October 20, 2026 (no platform-specific strftime codes)."""
    d = datetime.date.fromisoformat(iso)
    return f"{d:%B} {d.day}, {d.year}"


def write(rel: str, text: str) -> None:
    """Write a file under public/, creating folders."""
    p = PUBLIC / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def redirect(target: str) -> str:
    """Small page that sends old links to their new place."""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Redirecting</title>'
            f'<link rel="canonical" href="{target}"><meta http-equiv="refresh" content="0; url={target}"></head>'
            f'<body><p><a href="{target}">{target}</a></p></body></html>\n')


def email_link(addr: str) -> str:
    """mailto: written as character references, as on the old site."""
    return "".join(f"&#{ord(c)};" for c in "mailto:" + addr)


# ---------------------------------------------------------------- pages
def news_items() -> list:
    """Visible news items, newest first."""
    items = []
    for f in sorted((CONTENT / "news").glob("*.md")):
        meta, body = read_page(f)
        if meta.get("hidden", "").lower() in ("yes", "true"):
            continue
        items.append((meta["date"], f.name, inline(body.strip())))
    return sorted(items, reverse=True)


def news_table() -> str:
    rows = "".join(
        f"<tr><th>{datetime.date.fromisoformat(d).strftime('%b %d, %Y')}</th><td>{t}</td></tr>\n"
        for d, _, t in news_items())
    return f'<table class="news">\n{rows}</table>'


def build(today: str) -> list:
    """Write every page. Returns the list of page paths for the sitemap."""
    site = read_settings(CONTENT / "site.txt")
    icons = json.loads((ROOT / "tools" / "icons.json").read_text())
    pages = []

    # Home
    meta, body = read_page(CONTENT / "about.md")
    social = "".join(
        f'<a href="{email_link(site["email"]) if k == "email" else site[k]}" title="{label}">'
        f'<svg viewBox="{icons[k]["vb"]}" role="img" aria-label="{label}"><path d="{icons[k]["d"]}"/></svg></a>'
        for k, label in [("email", "email"), ("github", "GitHub"), ("linkedin", "LinkedIn"), ("orcid", "ORCID"), ("scholar", "Google Scholar")])
    home = f"""<h1>{site['name']}</h1>
<p class="subtitle">{meta['subtitle']}</p>
<img class="portrait" src="/assets/img/prof_pic.jpg" alt="{site['name']}" width="300" height="300">
<div class="prose">
{markdown(body)}
</div>
<div class="tc-band">
<img src="/assets/img/terra_cognita_lockup.svg" alt="Terra Cognita, Earth, Known" width="180" height="96">
<div class="copy"><h2>Consulting</h2><p>I run Terra Cognita LLC, a consulting firm for scientific computing, data analysis, and modeling.</p></div>
<a class="btn" href="{site['consulting_url']}">Visit Terra Cognita</a>
</div>
<h2>news</h2>
{news_table()}
<div class="social">{social}<p>{site['contact_note']}</p></div>"""
    write("index.html", frame(site, "about", home, "/", today, brand=False)); pages.append("/")

    # Publications
    meta, body = read_page(CONTENT / "publications.md")
    entries = parse_bib((CONTENT / "papers.bib").read_text(encoding="utf-8"))
    figure = ('<div class="figure"><img src="/assets/img/model_fixed.png" alt="Models under development: CMM in AMD fluids, '
              'CMM in AMD precipitants, CMM and AMD microbiology" width="1400" height="849" loading="lazy"></div>')
    pub = (f'<h1>publications</h1>\n<div class="prose">{markdown(body)}</div>\n{figure}\n'
           f'<input class="filter" type="search" placeholder="Type to filter" aria-label="Filter publications">\n'
           f'{publications_html(entries)}')
    write("publications/index.html", frame(site, "publications", pub, "/publications/", today, JS_PUBS)); pages.append("/publications/")

    # Tools
    tools = [(read_page(f)[0], f.stem) for f in sorted((CONTENT / "tools").glob("*.md"))]
    gh = icons["github"]
    parts = ['<h1>tools</h1>\n<p>Lab tools and calculators.</p>']
    for cat in ("software", "utilities"):
        cards = []
        for t, _ in sorted([x for x in tools if x[0]["category"] == cat], key=lambda x: int(x[0].get("order", 99))):
            ghl = (f'<span class="gh" title="GitHub repository"><svg viewBox="{gh["vb"]}" aria-hidden="true"><path d="{gh["d"]}"/></svg></span>'
                   if t.get("github") else "")
            cards.append(f'<a class="card" href="{t["page"]}"><img src="{t["thumb"]}" alt="{html.escape(t["title"])}" loading="lazy">'
                         f'<div class="body"><h3 class="name">{html.escape(t["title"])}</h3><p class="desc">{html.escape(t["description"])}</p>{ghl}</div></a>')
        parts.append(f'<h2 class="category" id="{cat}">{cat}</h2>\n<div class="cards">{"".join(cards)}</div>')
    write("tools/index.html", frame(site, "tools", "\n".join(parts), "/tools/", today)); pages.append("/tools/")
    for t, slug in tools:                       # old card links from the previous site
        write(f"projects/{slug}/index.html", redirect(t["page"]))

    # CV
    cv_pdf = sorted((PUBLIC / "assets" / "pdf").glob("terra_cv_*_web.pdf"))[-1].name
    cv_imgs = sorted((PUBLIC / "assets" / "img" / "cv").glob("*.png"), key=lambda p: int(re.search(r"_p(\d+)\.png$", p.name).group(1)))
    imgs = "\n".join(f'<img src="/assets/img/cv/{p.name}" alt="CV page {i} of {len(cv_imgs)}" width="1275" height="1650" loading="lazy">'
                     for i, p in enumerate(cv_imgs, 1))
    cv = (f'<h1>cv</h1>\n<p><a class="cv-download" href="/assets/pdf/{cv_pdf}">Download the CV (PDF)</a></p>\n'
          f'<div class="cv-pages">\n{imgs}\n</div>')
    write("cv/index.html", frame(site, "cv", cv, "/cv/", today)); pages.append("/cv/")

    # People
    meta, body = read_page(CONTENT / "people.md")
    write("people/index.html", frame(site, "people", f'<h1>people</h1>\n<div class="prose">{markdown(body)}</div>', "/people/", today))
    pages.append("/people/")

    # News
    write("news/index.html", frame(site, "news", f"<h1>news</h1>\n{news_table()}", "/news/", today)); pages.append("/news/")

    # Not found (GitHub Pages serves 404.html for missing paths)
    nf = ('<h1>Page not found</h1>\n<p>Nothing exists at this address. Go to the <a href="/">home page</a>.</p>')
    write("404.html", frame(site, "page not found", nf, "/404.html", today))

    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{site['url']}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in pages) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")
    write(".nojekyll", "")
    return pages


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    print("built", ", ".join(build(day)))
