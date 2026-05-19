from core.recovery.cleaner import structural_cleanup
from core.assets.recovery import recover_assets
from core.ai.repair import ai_repair
from core.ai.banner import inject_banner
from infrastructure.logging.logger import get_logger

log = get_logger("pipeline")


class RecoveryPipeline:
    """
    Full recovery pipeline:

    Raw HTML
        ↓ structural_cleanup   — remove dead JS, fix charset, set base URL
        ↓ recover_assets       — rewrite image/CSS URLs to Wayback versions
        ↓ ai_repair            — Claude semantic repair (skipped in raw mode)
        ↓ inject_banner        — DWN recovery banner
        → Final HTML
    """

    async def run(
        self,
        raw_html: str,
        url: str,
        archive_url: str,
        timestamp: str,
        mode: str = "historical",
        job_id: str = None,
    ) -> dict:

        log.info("Pipeline started", url=url, mode=mode, job_id=job_id)

        # Step 1 — Structural cleanup (always)
        cleaned = structural_cleanup(raw_html, archive_url)
        self._progress(job_id, 25)

        # Step 2 — Asset recovery (always)
        with_assets = recover_assets(cleaned, timestamp)
        self._progress(job_id, 50)

        if mode == "raw":
            final = inject_banner(with_assets, archive_url, url, mode="raw")
            return {"html": final, "mode": "raw"}

        # Step 3 — AI semantic repair
        repaired = ai_repair(with_assets, url)
        self._progress(job_id, 80)

        # Step 4 — Banner
        final = inject_banner(repaired, archive_url, url, mode=mode)
        self._progress(job_id, 100)

        log.info("Pipeline complete", url=url, mode=mode)
        return {"html": final, "mode": mode}

    def _progress(self, job_id: str | None, pct: int):
        if job_id:
            from infrastructure.db.repository import update_job
            update_job(job_id, "processing", progress=pct)
