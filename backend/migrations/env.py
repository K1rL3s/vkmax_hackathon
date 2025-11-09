import asyncio
import sys
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from maxhack.config import load_config
from maxhack.core.utils.datehelp import MOSCOW_TIMEZONE, datetime_now
from maxhack.infra.database.models.base import BaseAlchemyModel

try:
    db_config = load_config().db
except KeyError:
    db_config = load_config(".env").db

config = context.config
config.set_main_option("sqlalchemy.url", db_config.uri)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseAlchemyModel.metadata


def process_revision_directives(
    context: Any,
    revision: Any,
    directives: Any,
) -> None:
    migration_script = directives[0]
    now = datetime_now()
    migration_script.rev_id = now.astimezone(MOSCOW_TIMEZONE).strftime("%Y.%m.%d_%H.%M")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
