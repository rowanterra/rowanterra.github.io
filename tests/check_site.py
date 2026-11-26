"""Check the built site in public/ before it is published.

Checks: every local href and src points to a file that exists; no page loads a script, stylesheet,
font or image from another host; every page has the viewport tag, the top bar and one <h1>;
every sitemap entry exists. Links to other sites (<a href="https://...">) are allowed.
Run: python3 tests/check_site.py      (exit code 1 when anything fails)
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

PUBLIC = Path(__file__).resolve().parent.parent / "public"


class Refs(HTMLParser):
    """Collect (tag, attribute, value) for every href and src, plus page markers."""

    def __init__(self) -> None:
        super().__init__()
        self.refs, self.h1, self.viewport, self.bar = [], 0, False, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src"):
            if a.get(k):
                self.refs.append((tag, k, a[k], a.get("rel", "")))
        self.h1 += tag == "h1"
        self.viewport |= tag == "meta" and a.get("name") == "viewport"
        self.bar |= tag == "header" and "bar" in a.get("class", "")


def local_target(page: Path, value: str) -> Path:
    """File that a site-relative or page-relative link refers to."""
    path = unquote(urlparse(value).path)
    base = PUBLIC if path.startswith("/") else page.parent
    t = (base / path.lstrip("/")).resolve()
    return t / "index.html" if t.is_dir() or path.endswith("/") else t


def main() -> int:
    errors = []
    pages = sorted(p for p in PUBLIC.rglob("*.html") if "assets" not in p.relative_to(PUBLIC).parts)
    for page in pages:
        r = Refs()
        r.feed(page.read_text(encoding="utf-8"))
        rel = page.relative_to(PUBLIC)
        redirect_page = "http-equiv" in page.read_text(encoding="utf-8")
        if not redirect_page:
            if not r.viewport:
                errors.append(f"{rel}: no viewport tag")
            if not r.bar:
                errors.append(f"{rel}: no top bar")
            if r.h1 != 1:
                errors.append(f"{rel}: {r.h1} <h1> elements")
        for tag, attr, value, relattr in r.refs:
            scheme = urlparse(value).scheme
            if scheme in ("mailto", "") and value.startswith(("&#", "mailto:")):
                continue
            if scheme in ("http", "https"):
                if tag != "a" and relattr != "canonical":
                    errors.append(f"{rel}: external {tag} {attr}={value}")
                continue
            if value.startswith("#"):
                continue
            if not local_target(page, value).exists():
                errors.append(f"{rel}: missing {value}")
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    for loc in re.findall(r"<loc>https?://[^/]+(/[^<]*)</loc>", sitemap):
        if not local_target(PUBLIC / "index.html", loc).exists():
            errors.append(f"sitemap: missing {loc}")
    for e in errors:
        print(e)
    print(f"{len(pages)} pages checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
