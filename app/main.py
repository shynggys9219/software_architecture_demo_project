from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings
from app.di import Container
from app.adapters.http.health_router import router as health_router
from app.adapters.http.auth_router import router as auth_router
from app.adapters.http.items_router import router as items_router

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, swagger_ui_parameters={"persistAuthorization": True})
    app.container = Container()  # type: ignore[attr-defined]

    @app.on_event("startup")
    async def _startup():
        try:
            d = await app.container.db.db()
            await d.command("ping")
        except Exception:
            pass

    # CORS
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(items_router, prefix="/items", tags=["items"])
    return app

app = create_app()