import asyncio
from typing import Callable
from infrastructure.logging.logger import get_logger
from infrastructure.db.repository import update_job

log = get_logger("queue")


class JobQueue:
    """
    Async in-process job queue.
    Designed to be replaced by Celery+Redis in production.
    Tracks job lifecycle: queued → processing → completed | failed
    """

    def __init__(self, max_workers: int = 3):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._max_workers = max_workers
        self._running = False
        self._tasks: list[asyncio.Task] = []         # Fix 9 — tracks active worker tasks

    async def start(self):
        self._running = True
        self._tasks = [
            asyncio.create_task(self._worker())
            for _ in range(self._max_workers)
        ]
        log.info("Job queue started", workers=self._max_workers)

    async def stop(self):
        self._running = False
        await self._queue.join()
        for task in self._tasks:
            task.cancel()

    async def enqueue(self, job_id: str, fn: Callable, **kwargs):
        await self._queue.put((job_id, fn, kwargs))
        log.info("Job enqueued", job_id=job_id)

    async def _worker(self):
        while self._running:
            try:
                job_id, fn, kwargs = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            update_job(job_id, "processing", progress=0)
            log.info("Job started", job_id=job_id)

            try:
                result = await fn(job_id=job_id, **kwargs)
                update_job(job_id, "completed", progress=100, result_id=result)
                log.info("Job completed", job_id=job_id)
            except Exception as e:
                update_job(job_id, "failed", error=str(e))
                log.error("Job failed", job_id=job_id, error=str(e))
            finally:
                self._queue.task_done()


job_queue = JobQueue()
