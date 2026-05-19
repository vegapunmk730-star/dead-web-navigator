from fastapi import APIRouter, HTTPException
from infrastructure.db.repository import get_history, get_job, get_jobs
from infrastructure.cache.memory_cache import cache
from core.recovery.providers.wayback import wayback

router = APIRouter()


@router.get("/history")
def history(limit: int = 20):
    return {"history": get_history(limit)}


@router.get("/health")
def health():
    return {
        "status":    "ok",
        "version":   "4.0.0",
        "service":   "Dead Web Navigator",
        "providers": {"wayback": wayback.health()},
        "cache":     cache.metrics(),
    }


@router.get("/metrics")
def metrics():
    return {"cache": cache.metrics(), "jobs": get_jobs(10)}


@router.get("/jobs")
def jobs(limit: int = 20):
    return {"jobs": get_jobs(limit)}


@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return job
