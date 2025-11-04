from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}

def get_db(request):
    return request.app.container.db  # type: ignore[attr-defined]

@router.get("/health/db")
async def health_db(db=Depends(get_db)):
    try:
        d = await db.db()
        await d.command("ping")
        return {"db": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="db_unavailable")