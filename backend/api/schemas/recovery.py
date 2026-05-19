from pydantic import BaseModel
from typing import Optional


class SnapshotScore(BaseModel):
    total: float
    html_integrity: float
    css_integrity: float
    asset_integrity: float
    semantic_richness: float
    link_survival: float
    grade: str


class SemanticInfo(BaseModel):
    title: Optional[str]
    headings: list
    links: list
    images: list
    forms: int
    text_length: int
    layout_type: str


class RecoveryResponse(BaseModel):
    status: str
    original_url: str
    snapshot_url: str
    timestamp: str
    year: str
    date: str
    html: str
    mode: str
    fingerprint: str
    confidence: float
    semantic: Optional[SemanticInfo]
    score: Optional[SnapshotScore]
    cached: bool


class TimelineResponse(BaseModel):
    url: str
    snapshots: list
    total: int


class HistoryResponse(BaseModel):
    history: list


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
    providers: dict
    cache: dict


class JobResponse(BaseModel):
    id: str
    url: str
    year: Optional[int]
    mode: str
    status: str
    progress: int
    result_id: Optional[str]
    error: Optional[str]
    created_at: str
    updated_at: str
