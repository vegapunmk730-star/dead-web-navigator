import httpx
from config.settings import settings
from infrastructure.logging.logger import get_logger

log = get_logger("fetcher")
HEADERS = {"User-Agent": "DeadWebNavigator/3.0"}


async def fetch_html(url: str) -> str | None:
    """Async fetch — non-blocking, safe for FastAPI event loop."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=settings.fetch_timeout) as client:
            r = await client.get(url, headers=HEADERS)
            r.encoding = r.apparent_encoding or "utf-8"
            log.info("Fetched", url=url, status=r.status_code, size=len(r.text))
            return r.text
    except Exception as e:
        log.error("Fetch failed", url=url, error=str(e))
        return None
