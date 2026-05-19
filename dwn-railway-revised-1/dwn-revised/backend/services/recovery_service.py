from core.recovery.providers.wayback import wayback
from core.recovery.fetcher import fetch_html
from core.engine.pipeline import RecoveryPipeline
from core.engine.semantic import extract_semantic
from core.engine.confidence import compute_confidence, compute_snapshot_score
from core.engine.fingerprint import fingerprint
from infrastructure.cache.memory_cache import cache
from infrastructure.db.repository import upsert_recovery  # Fix 8 — removed unused get_by_fingerprint
from infrastructure.logging.logger import get_logger

log = get_logger("recovery_service")
_pipeline = RecoveryPipeline()


class RecoveryService:

    async def recover(self, url: str, year: int = None, mode: str = "historical", job_id: str = None) -> dict:
        url = self._normalize(url)
        log.info("Recovery requested", url=url, year=year, mode=mode)

        cache_key = f"recover:{url}:{year}:{mode}"
        cached = cache.get(cache_key)
        if cached:
            log.info("Cache hit", url=url)
            return {**cached, "cached": True, "html": "[cached]"}

        snapshot = await wayback.get_best_snapshot(url, year)
        if not snapshot:
            raise ValueError(f"No snapshot found for: {url}")

        raw_html = await fetch_html(snapshot["archive_url"])
        if not raw_html:
            raise ConnectionError("Failed to fetch snapshot content.")

        fp = fingerprint(raw_html)

        result = await _pipeline.run(
            raw_html=raw_html,
            url=url,
            archive_url=snapshot["archive_url"],
            timestamp=snapshot["timestamp"],
            mode=mode,
            job_id=job_id,
        )

        semantic   = extract_semantic(raw_html)
        confidence = compute_confidence(raw_html, result["html"])
        score      = compute_snapshot_score(raw_html)

        upsert_recovery(
            url=url,
            timestamp=snapshot["timestamp"],
            archive_url=snapshot["archive_url"],
            fingerprint=fp,
            confidence=confidence,
            layout_type=semantic.get("layout_type", "generic"),
            mode=mode,
        )

        response = {
            "status":       "ok",
            "original_url": url,
            "snapshot_url": snapshot["archive_url"],
            "timestamp":    snapshot["timestamp"],
            "year":         snapshot["year"],
            "date":         snapshot["date"],
            "html":         result["html"],
            "mode":         mode,
            "fingerprint":  fp,
            "confidence":   confidence,
            "semantic":     semantic,
            "score":        score,
            "cached":       False,
        }

        cache.set(cache_key, {k: v for k, v in response.items() if k != "html"})
        log.info("Recovery complete", url=url, year=snapshot["year"], confidence=confidence)
        return response

    async def timeline(self, url: str) -> dict:
        url = self._normalize(url)
        cache_key = f"timeline:{url}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        snapshots = await wayback.get_timeline(url)
        if not snapshots:
            raise ValueError(f"No timeline for: {url}")
        result = {"url": url, "snapshots": snapshots, "total": len(snapshots)}
        cache.set(cache_key, result)
        return result

    async def compare(self, url: str, year_a: int, year_b: int) -> dict:
        url = self._normalize(url)
        snap_a = await wayback.get_best_snapshot(url, year_a)
        snap_b = await wayback.get_best_snapshot(url, year_b)
        if not snap_a or not snap_b:
            raise ValueError("One or both snapshots not found.")
        html_a = await fetch_html(snap_a["archive_url"]) or ""
        html_b = await fetch_html(snap_b["archive_url"]) or ""
        sem_a  = extract_semantic(html_a)
        sem_b  = extract_semantic(html_b)
        return {
            "url":       url,
            "version_a": {"year": str(year_a), "semantic": sem_a, "snapshot": snap_a["archive_url"]},
            "version_b": {"year": str(year_b), "semantic": sem_b, "snapshot": snap_b["archive_url"]},
            "diff": {
                "title_changed":  sem_a.get("title")       != sem_b.get("title"),
                "layout_changed": sem_a.get("layout_type") != sem_b.get("layout_type"),
                "headings_delta": len(sem_b.get("headings",[])) - len(sem_a.get("headings",[])),
                "links_delta":    len(sem_b.get("links",[]))    - len(sem_a.get("links",[])),
                "images_delta":   len(sem_b.get("images",[]))   - len(sem_a.get("images",[])),
                "text_delta":     sem_b.get("text_length",0)    - sem_a.get("text_length",0),
            }
        }

    @staticmethod
    def _normalize(url: str) -> str:
        url = url.strip()
        url = url.replace("https://https://", "https://")
        url = url.replace("http://http://", "http://")
        if not url.startswith("http"):
            url = "https://" + url
        return url


recovery_service = RecoveryService()
