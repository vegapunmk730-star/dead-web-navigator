# ◈ Dead Web Navigator v3.0

Motor de reconstrução histórica da web — arquitetura de engenharia real.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11 + FastAPI |
| AI | Anthropic Claude |
| Recovery | Internet Archive CDX API |
| Storage | SQLite (WAL mode) |
| Cache | In-memory LRU + TTL |
| Frontend | React 18 + Vite |
| Deploy | Docker + Railway |

---

## Arquitetura

```
backend/
├── main.py                          # Entry point
├── config/settings.py               # Configuração centralizada
├── api/routes/
│   ├── recover.py                   # /recover /timeline /compare
│   └── system.py                    # /health /metrics /history /jobs
├── core/
│   ├── recovery/
│   │   ├── providers/wayback.py     # Internet Archive
│   │   ├── fetcher.py               # HTTP fetcher
│   │   └── cleaner.py               # Structural cleanup
│   ├── assets/recovery.py           # Asset URL rewriting
│   ├── ai/
│   │   ├── repair.py                # Claude AI repair
│   │   └── banner.py                # Recovery banner
│   └── engine/
│       ├── pipeline.py              # Full recovery pipeline
│       ├── semantic.py              # Semantic extraction + layout classifier
│       ├── confidence.py            # Confidence + quality scoring
│       └── fingerprint.py           # SHA-256 deduplication
└── infrastructure/
    ├── cache/memory_cache.py        # LRU cache with metrics
    ├── db/repository.py             # SQLite repository
    ├── queue/job_queue.py           # Async job queue
    └── logging/logger.py            # Structured JSON logging
```

---

## Deploy Railway

1. Upload para GitHub (ficheiros extraídos, não o ZIP)
2. Railway → New Project → Deploy from GitHub
3. Variables → `ANTHROPIC_API_KEY = sk-ant-...`
4. Deploy automático via Dockerfile

---

## Correr localmente

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install && npm run dev
```

---

## API Endpoints

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/recover?url=&mode=historical` | Recuperar página |
| `GET /api/recover?url=&year=2010` | Ano específico |
| `GET /api/timeline?url=` | Anos disponíveis |
| `GET /api/compare?url=&year_a=&year_b=` | Comparar versões |
| `GET /api/history` | Histórico |
| `GET /api/health` | Status + providers |
| `GET /api/metrics` | Cache + jobs |
| `GET /api/docs` | Swagger UI |

---

**Dead Web Navigator v3.0** — Francisco & Clénio Abreu
