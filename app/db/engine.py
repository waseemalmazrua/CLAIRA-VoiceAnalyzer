from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

engine: AsyncEngine = create_async_engine(
    str(settings.database_url),
    echo=False,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,
    },
)
