import httpx
from infrastructure.logging.logger import get_logger

log = get_logger("wayback")

CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK  = "https://web.archive.org/web"
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; DeadWebNavigator/4.0)"}


class WaybackProvider:

    name = "wayback"

    async def get_best_snapshot(self, url: str, year: int = None) -> dict | None:
        for target in self._url_variants(url):
            result = await self._fetch_snapshot(target, year)
            if result:
                return result
        return None

    async def _fetch_snapshot(self, url: str, year: int = None, _retried: bool = False) -> dict | None:
        params = {
            "url": url, "output": "json", "limit": 1,
            "filter": "statuscode:200", "fl": "timestamp,original", "collapse": "digest",
        }
        if year:
            params["from"] = f"{year}0101"
            params["to"]   = f"{year}1231"

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(CDX_API, params=params, headers=HEADERS)
                data = r.json()
        except Exception as e:
            log.error("CDX error", error=str(e), url=url)
            return None

        if len(data) < 2:
            # Retry without year filter — only once
            if year and not _retried:
                return await self._fetch_snapshot(url, year=None, _retried=True)
            return None

        ts, original = data[1][0], data[1][1]
        return self._build(ts, original)

    async def get_timeline(self, url: str) -> list:
        results = []
        for target in self._url_variants(url):
            params = {
                "url": target, "output": "json",
                "fl": "timestamp,statuscode", "filter": "statuscode:200",
                "collapse": "timestamp:4", "limit": 50,
            }
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    r = await client.get(CDX_API, params=params, headers=HEADERS)
                    data = r.json()
                    if len(data) >= 2:
                        results = [self._build(row[0], target) for row in data[1:]]
                        break
            except Exception as e:
                log.error("Timeline error", error=str(e))
        return results

    def _url_variants(self, url: str) -> list:
        variants = [url]
        if "://www." not in url:
            variants.append(url.replace("://", "://www."))
        if "://www." in url:
            variants.append(url.replace("://www.", "://"))
        return variants

    def _build(self, timestamp: str, original: str) -> dict:
        return {
            "provider":     self.name,
            "timestamp":    timestamp,
            "original_url": original,
            "archive_url":  f"{WAYBACK}/{timestamp}id_/{original}",
            "year":         timestamp[:4],
            "date":         f"{timestamp[6:8]}/{timestamp[4:6]}/{timestamp[:4]}",
        }

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get("https://web.archive.org")
                return r.status_code < 500
        except:
            return False


wayback = WaybackProvider()
