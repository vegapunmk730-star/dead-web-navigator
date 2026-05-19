import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str  = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    ai_model: str           = "claude-opus-4-5"
    ai_max_tokens: int      = 4096
    ai_html_trim: int       = 10_000
    wayback_timeout: int    = 20
    fetch_timeout: int      = 25
    port: int               = field(default_factory=lambda: int(os.getenv("PORT", 8000)))
    debug: bool             = field(default_factory=lambda: os.getenv("DEBUG","false").lower()=="true")
    db_path: str            = field(default_factory=lambda: os.getenv("DB_PATH", "/app/data/deadweb.db"))
    w_html: float           = 0.35
    w_css: float            = 0.20
    w_assets: float         = 0.20
    w_semantic: float       = 0.15
    w_links: float          = 0.10


settings = Settings()
