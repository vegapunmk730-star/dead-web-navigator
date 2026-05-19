from fastapi import APIRouter, HTTPException
from typing import Optional
from services.recovery_service import recovery_service

router = APIRouter()


@router.get("/recover")
async def recover(url: str, year: Optional[int] = None, mode: str = "historical"):
    try:
        return await recovery_service.recover(url=url, year=year, mode=mode)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except ConnectionError as e:
        raise HTTPException(502, str(e))
    except Exception as e:
        raise HTTPException(500, f"Recovery error: {str(e)}")


@router.get("/timeline")
async def timeline(url: str):
    try:
        return await recovery_service.timeline(url)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Timeline error: {str(e)}")


@router.get("/compare")
async def compare(url: str, year_a: int, year_b: int):
    try:
        return await recovery_service.compare(url, year_a, year_b)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Compare error: {str(e)}")
