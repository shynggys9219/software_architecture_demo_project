from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.db import Database

router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}

def get_db(request: Request) -> Database:  # ← type matters
    return request.app.container.db  # type: ignore[attr-defined]

@router.get("/health/db")
async def health_db(db: Database = Depends(get_db)):
    try:
        d = await db.db()
        await d.command("ping")
        return {"db": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="db_unavailable")