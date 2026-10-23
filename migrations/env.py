import asyncio
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from app.core.config import settings

# مهم: هذا الاستيراد يسجل Profile و auth.users
# داخل SQLModel.metadata.
from app.db.models import Profile  # noqa: F401

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    str(settings.database_url).replace("%", "%%"),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = SQLModel.metadata


def include_object(
    object_: Any,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """
    استبعاد الجداول الخارجية التي نعرّفها داخل metadata
    فقط لحل العلاقات، لكن لا نريد من Alembic إنشاؤها
    أو تعديلها.

    مثال:
        auth.users
    """

    return not (
        type_ == "table"
        and not reflected
        and object_.info.get("skip_autogenerate", False)
    )


def configure_context(
    *,
    connection: Connection | None = None,
    url: str | None = None,
) -> None:
    """
    إعداد Alembic بطريقة موحدة للـoffline والـonline modes.
    """

    common_options = {
        "target_metadata": target_metadata,
        "compare_type": True,
        "include_object": include_object,
    }

    if connection is not None:
        context.configure(
            connection=connection,
            **common_options,
        )
        return

    if url is None:
        raise ValueError("A database connection or URL must be provided.")

    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        **common_options,
    )


def run_migrations_offline() -> None:
    """
    تشغيل migrations بدون فتح اتصال فعلي بقاعدة البيانات.

    يُستخدم مثلًا عند توليد SQL فقط.
    """

    url = config.get_main_option("sqlalchemy.url")

    if not url:
        raise RuntimeError("SQLAlchemy database URL is not configured.")

    configure_context(url=url)

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    تشغيل migrations باستخدام اتصال SQLAlchemy فعلي.
    """

    configure_context(connection=connection)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    إنشاء AsyncEngine مخصص لـAlembic وتشغيل migration.
    """

    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={
            "statement_cache_size": 0,
        },
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """
    نقطة تشغيل migrations في الوضع المتصل بقاعدة البيانات.
    """

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
