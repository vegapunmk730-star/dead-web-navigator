import sqlite3
import os
import uuid
from typing import Optional
from config.settings import settings
from infrastructure.logging.logger import get_logger

log = get_logger("db")
_DB = os.path.abspath(settings.db_path)


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_DB), exist_ok=True)
    c = sqlite3.connect(_DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=NORMAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init_db() -> None:
    conn = _conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS recoveries (
            id          TEXT PRIMARY KEY,
            url         TEXT NOT NULL,
            timestamp   TEXT,
            archive_url TEXT,
            fingerprint TEXT,
            confidence  REAL DEFAULT 0,
            layout_type TEXT DEFAULT 'generic',
            mode        TEXT DEFAULT 'historical',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id          TEXT PRIMARY KEY,
            url         TEXT NOT NULL,
            year        INTEGER,
            mode        TEXT DEFAULT 'historical',
            status      TEXT DEFAULT 'queued',
            progress    INTEGER DEFAULT 0,
            result_id   TEXT,
            error       TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_rec_url ON recoveries(url);
        CREATE INDEX IF NOT EXISTS idx_rec_fp  ON recoveries(fingerprint);
        CREATE INDEX IF NOT EXISTS idx_job_st  ON jobs(status);
    """)
    conn.commit()
    conn.close()
    log.info("DB ready", path=_DB)


def save_recovery(url, timestamp, archive_url, fingerprint=None, confidence=0, layout_type="generic", mode="historical") -> str:
    rid = str(uuid.uuid4())
    conn = _conn()
    conn.execute(
        "INSERT OR IGNORE INTO recoveries (id,url,timestamp,archive_url,fingerprint,confidence,layout_type,mode) VALUES (?,?,?,?,?,?,?,?)",
        (rid, url, timestamp, archive_url, fingerprint, confidence, layout_type, mode)
    )
    conn.commit()
    conn.close()
    return rid


# Alias — recovery_service.py uses this name
def upsert_recovery(url, timestamp, archive_url, fingerprint=None, confidence=0, layout_type="generic", mode="historical") -> str:
    return save_recovery(url, timestamp, archive_url, fingerprint, confidence, layout_type, mode)


def get_history(limit: int = 20) -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT url,timestamp,archive_url,confidence,layout_type,mode,created_at FROM recoveries ORDER BY rowid DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_by_fingerprint(fp: str) -> Optional[dict]:
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM recoveries WHERE fingerprint=? LIMIT 1", (fp,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_job(url: str, year: Optional[int], mode: str) -> str:
    jid = str(uuid.uuid4())
    conn = _conn()
    conn.execute("INSERT INTO jobs (id,url,year,mode) VALUES (?,?,?,?)", (jid, url, year, mode))
    conn.commit()
    conn.close()
    return jid


def update_job(jid: str, status: str, progress: int = None, result_id: str = None, error: str = None) -> None:
    sets = ["status=?", "updated_at=datetime('now')"]
    vals = [status]
    if progress is not None: sets.append("progress=?"); vals.append(progress)
    if result_id:            sets.append("result_id=?"); vals.append(result_id)
    if error:                sets.append("error=?");     vals.append(error)
    vals.append(jid)
    conn = _conn()
    conn.execute(f"UPDATE jobs SET {','.join(sets)} WHERE id=?", vals)
    conn.commit()
    conn.close()


def get_job(jid: str) -> Optional[dict]:
    conn = _conn()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_jobs(limit: int = 50) -> list:
    conn = _conn()
    rows = conn.execute("SELECT * FROM jobs ORDER BY rowid DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
