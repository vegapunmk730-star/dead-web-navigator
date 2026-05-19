from bs4 import BeautifulSoup


def extract_semantic(html: str) -> dict:
    if not html:
        return {}
    soup = BeautifulSoup(html, "lxml")
    return {
        "title":       soup.title.get_text(strip=True) if soup.title else None,
        "headings":    [{"tag": h.name, "text": h.get_text(strip=True)[:100]} for h in soup.find_all(["h1","h2","h3"])][:20],
        "links":       [a["href"] for a in soup.find_all("a", href=True) if not a["href"].startswith("#")][:40],
        "images":      [i["src"] for i in soup.find_all("img", src=True)][:20],
        "forms":       len(soup.find_all("form")),
        "text_length": len(soup.get_text(strip=True)),
        "layout_type": classify_layout(soup),
    }


def classify_layout(soup_or_html) -> str:
    if isinstance(soup_or_html, str):
        soup = BeautifulSoup(soup_or_html, "lxml")
    else:
        soup = soup_or_html
    text = str(soup).lower()

    if soup.find("article") or any(k in text for k in ["breaking news","editorial","headline"]):
        return "news"
    if soup.find(class_=lambda x: x and "post" in str(x).lower()):
        return "blog"
    if any(k in text for k in ["forum","thread","reply","topic","post #","membre"]):
        return "forum"
    if any(k in text for k in ["add to cart","buy now","checkout","shopping cart","produto"]):
        return "ecommerce"
    if len(soup.find_all("a")) > 80:
        return "portal"
    if len(soup.find_all("table")) > 5:
        return "old_web"
    return "generic"
