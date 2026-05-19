from bs4 import BeautifulSoup
from infrastructure.logging.logger import get_logger

log = get_logger("cleaner")

DEAD_ATTRS = ["onclick", "onload", "onerror", "onmouseover", "data-track", "data-ga", "data-analytics"]


def structural_cleanup(html: str, base_url: str = "") -> str:
    soup = BeautifulSoup(html, "lxml")

    # Remove dead scripts + noscript
    for tag in soup(["script", "noscript"]):
        tag.decompose()

    # Remove Wayback toolbar injection
    for tag in soup.find_all(id=lambda x: x and ("wm-" in x.lower() or "wayback" in x.lower())):
        tag.decompose()
    for tag in soup.find_all(class_=lambda x: x and "wb-" in str(x).lower()):
        tag.decompose()

    # Remove iframes
    for tag in soup.find_all("iframe"):
        tag.decompose()

    # Ensure head
    if not soup.head:
        head = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head)

    # Ensure charset
    if soup.head and not soup.head.find("meta", charset=True):
        meta = soup.new_tag("meta", charset="utf-8")
        soup.head.insert(0, meta)

    # Base URL for relative asset resolution
    if base_url and soup.head:
        for b in soup.head.find_all("base"):
            b.decompose()
        soup.head.insert(1, soup.new_tag("base", href=base_url))

    # Strip tracking attributes
    for tag in soup.find_all(True):
        for attr in DEAD_ATTRS:
            tag.attrs.pop(attr, None)

    log.info("Structural cleanup done")
    return str(soup)
