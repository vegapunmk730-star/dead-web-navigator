import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from infrastructure.db.repository import init_db
from infrastructure.queue.job_queue import job_queue
from infrastructure.logging.logger import get_logger
from api.routes.recover import router as recover_router
from api.routes.system  import router as system_router

log = get_logger("main")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await job_queue.start()                          # Fix 10 — queue now starts
    log.info("Dead Web Navigator v4.0 started", port=settings.port)
    yield
    await job_queue.stop()


app = FastAPI(
    title="Dead Web Navigator",
    version="4.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                             # TODO: restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recover_router, prefix="/api", tags=["Recovery"])
app.include_router(system_router,  prefix="/api", tags=["System"])


@app.get("/", response_class=HTMLResponse)
async def root():
    index = os.path.join(STATIC_DIR, "index.html")
    with open(index, encoding="utf-8") as f:         # Fix 3 — file properly closed
        return f.read()
