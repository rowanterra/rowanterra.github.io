"""Check the visible copy of a page for AI-style wording.

Input: an HTML file. Reads visible text, alt and title attributes, option labels and the meta description;
skips <style>, <script> and <svg>.
Run: python3 lint_copy.py index.html   (exit code 1 when anything is found)
Each hit prints the rule, the matched text and its sentence. Edit the lists below to add words.
"""
import re
import sys
from html.parser import HTMLParser

# Figurative or business verbs: the literal sense is rare on a consulting site, so every hit gets read by hand
VERBS = r"land|lands|landed|ship|ships|shipped|drive|drives|driven|engine|own|owns|wield|spearhead|champion|leverage|harness|navigate|unpack|streamline|elevate|foster|delve|carry|carries|carried|flag|flags|flagged|hold|holds|sit|sits|ride|rides|anchor|unlock|empower|craft|crafted|tailored|bespoke|journey|partner with"
GRADING = r"seamless|seamlessly|robust|comprehensive|powerful|intricate|holistic|cutting-edge|state-of-the-art|game-changing|revolutionary|best-in-class|world-class|innovative|actionable|curated|end-to-end|turnkey|unparalleled|trusted|passionate|dedicated|expert|expertise|insights|solutions|data-driven|deep dive|landscape|ecosystem|paradigm|synergy|learnings|north star|table stakes"
FILLER = r"aspects|elements|factors|considerations|nuances|dynamics|a wide range of|a variety of|a myriad of|a plethora of|numerous|various|significantly|substantially|truly|genuinely|honestly|straightforward|simply put|at its core|in essence|ultimately|moreover|furthermore|additionally|importantly|it's worth noting|whether you're|from .{1,30} to .{1,30} and beyond"
SCAFFOLDS = [
    (r"\bnot (just|only) [^.]{1,60}, but\b", "antithesis pair"),
    (r"\bisn't about\b|\bis not about\b", "antithesis pair"),
    (r"\?\s+[A-Z][^.?!]{0,40}\.", "rhetorical question then answer"),
    (r"\b[Tt]he \w+(?: \w+)?, the \w+", "the X, the Y list"),
    (r"—", "em dash"),
    (r"(?<!\d)–|–(?!\d)", "en dash outside a range"),
    (r"!", "exclamation point"),
    (r"\byou\b|\byour\b", "second person (allowed only in form labels; read each hit)"),
    (r"\b(One|Two|Three|Four|Five) [a-z]+(, (one|two|three) [a-z]+)?\.", "counted slogan"),
    (r"\b\w+ly\b,? (and|but) \w+ly\b", "adverb pair"),
]


class Text(HTMLParser):
    """Collect visible text and the attributes a reader sees."""
    SKIP = {"style", "script", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self.depth, self.parts = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1
        a = dict(attrs)
        for k in ("alt", "title", "aria-label", "placeholder"):
            if a.get(k):
                self.parts.append(a[k])
        if tag == "meta" and a.get("name") == "description":
            self.parts.append(a.get("content", ""))

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth == 0 and data.strip():
            self.parts.append(data.strip())


ALLOW = [r"critical elements", r"rare earth elements"]  # literal chemistry


def hits(text: str):
    """Yield (rule, match, context) for each finding."""
    for a in ALLOW:
        text = re.sub(a, lambda m: "x" * len(m.group(0)), text, flags=re.I)
    # comma-chained fragments such as "Question, data, limits." (short, no verb, ends in a period)
    for m in re.finditer(r"(?:^|[|.]\s*)([A-Z][^.|]{0,60}\.)", text):
        s = m.group(1)
        if len(s.split()) <= 6 and "," in s and not re.search(r"\b(is|are|was|were|has|have|come|comes|needs|need)\b", s):
            yield "comma-chained fragment", s, s
    for name, pat in (("verb", VERBS), ("grading or cliche", GRADING), ("filler", FILLER)):
        for m in re.finditer(rf"\b({pat})\b", text, flags=re.I):
            yield name, m.group(0), text[max(0, m.start() - 50): m.end() + 50]
    for pat, name in SCAFFOLDS:
        for m in re.finditer(pat, text):
            yield name, m.group(0), text[max(0, m.start() - 50): m.end() + 50]


def main(path: str) -> int:
    p = Text()
    p.feed(open(path, encoding="utf-8").read())
    text = " | ".join(p.parts)
    found = list(hits(text))
    for rule, m, ctx in found:
        print(f"[{rule}] '{m}'  ...{ctx}...")
    print(f"{len(found)} findings in {len(text.split())} words")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
