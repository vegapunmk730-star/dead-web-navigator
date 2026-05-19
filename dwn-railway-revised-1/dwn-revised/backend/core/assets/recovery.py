from bs4 import BeautifulSoup
from infrastructure.logging.logger import get_logger

log = get_logger("assets")
WAYBACK = "https://web.archive.org/web"


def recover_assets(html: str, timestamp: str) -> str:
    """
    Rewrite broken asset URLs to Wayback Machine versions.
    Covers: images, stylesheets, favicons.
    Note: onerror fallback removed to avoid reintroducing inline JS
    after structural_cleanup. Missing assets degrade gracefully via CSS.
    """
    soup = BeautifulSoup(html, "lxml")
    recovered = 0

    # Images                                         # Fix 5 — onerror removed
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if _is_rewritable(src):
            img["src"] = _wayback_url(src, timestamp)
            img["loading"] = "lazy"
            recovered += 1

    # CSS links
    for link in soup.find_all("link", rel=lambda r: r and "stylesheet" in r):
        href = link.get("href", "")
        if _is_rewritable(href):
            link["href"] = _wayback_url(href, timestamp)
            recovered += 1

    # Favicons
    for link in soup.find_all("link", rel=lambda r: r and "icon" in str(r).lower()):
        href = link.get("href", "")
        if _is_rewritable(href):
            link["href"] = _wayback_url(href, timestamp)

    log.info("Asset recovery done", recovered=recovered)
    return str(soup)


def _is_rewritable(url: str) -> bool:
    return bool(url and url.startswith("http") and "web.archive.org" not in url)


def _wayback_url(url: str, timestamp: str) -> str:
    return f"{WAYBACK}/{timestamp}if_/{url}"
