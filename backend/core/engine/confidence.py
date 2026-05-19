"""
Confidence and quality scoring.
FIX v4: BeautifulSoup parsed ONCE per document, not 8x.
"""
from bs4 import BeautifulSoup
from config.settings import settings


def _parse(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def compute_confidence(original: str, reconstructed: str) -> float:
    orig  = _parse(original)
    recon = _parse(reconstructed)
    s = settings
    score = (
        _html_integrity(orig, recon)  * s.w_html     +
        _css_integrity(orig, recon)   * s.w_css      +
        _semantic_match(orig, recon)  * s.w_semantic  +
        _link_survival(orig, recon)   * s.w_links
    )
    return round(min(max(score, 0.0), 1.0), 4)


def compute_snapshot_score(html: str) -> dict:
    soup = _parse(html)
    s = settings
    h   = _html_score(soup)
    c   = _css_score(soup)
    a   = _asset_score(soup)
    sem = _semantic_score(soup)
    l   = _link_score(soup)
    total = h*s.w_html + c*s.w_css + a*s.w_assets + sem*s.w_semantic + l*s.w_links
    return {
        "total":             round(total, 3),
        "html_integrity":    round(h, 3),
        "css_integrity":     round(c, 3),
        "asset_integrity":   round(a, 3),
        "semantic_richness": round(sem, 3),
        "link_survival":     round(l, 3),
        "grade":             _grade(total),
    }


def _html_integrity(o, r):
    a, b = len(o.find_all()), len(r.find_all())
    return min(b/a, 1.0) if a else 0.5

def _css_integrity(o, r):
    a = len(o.find_all("style"))
    b = len(r.find_all("style"))
    return min(b/a, 1.0) if a else 0.8

def _semantic_match(o, r):
    a = set(o.get_text().split()[:200])
    b = set(r.get_text().split()[:200])
    return len(a&b)/len(a) if a else 0.0

def _link_survival(o, r):
    a = {x["href"] for x in o.find_all("a",href=True)}
    b = {x["href"] for x in r.find_all("a",href=True)}
    return len(a&b)/len(a) if a else 1.0

def _html_score(soup):
    score = min(len(soup.find_all())/50, 1.0)
    if soup.head and soup.body: score = min(score+0.15, 1.0)
    return score

def _css_score(soup):
    return min((len(soup.find_all("style")) + len(soup.find_all("link", rel=lambda r: r and "stylesheet" in r)))/3, 1.0)

def _asset_score(soup):
    imgs = soup.find_all("img", src=True)
    if not imgs: return 0.5
    return sum(1 for i in imgs if not i["src"].startswith("data:"))/len(imgs)

def _semantic_score(soup):
    s = 0.0
    if soup.title: s += 0.3
    if soup.find_all(["h1","h2","h3"]): s += 0.3
    if soup.find("article") or soup.find("main"): s += 0.2
    if len(soup.get_text(strip=True)) > 500: s += 0.2
    return min(s, 1.0)

def _link_score(soup):
    return min(len(soup.find_all("a",href=True))/20, 1.0)

def _grade(score):
    if score >= 0.85: return "A"
    if score >= 0.70: return "B"
    if score >= 0.55: return "C"
    if score >= 0.40: return "D"
    return "F"
