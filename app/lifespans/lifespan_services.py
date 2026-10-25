from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.engine import engine
from app.lifespans.services import Services


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.services = Services()

    # اختياري: تأكد أن Redis متصل قبل بدء استقبال الطلبات
    await app.state.services.redis.ping()

    try:
        yield
    finally:
        app.state.services.whisper.aclose()
        await app.state.services.ner.aclose()
        await app.state.services.redis.aclose()
        await engine.dispose()
