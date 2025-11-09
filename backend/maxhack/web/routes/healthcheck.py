"""Эндпоинт для проверки работоспособности сервиса."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.infra.database.database_connection import db_async_session

healthcheck_router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@healthcheck_router.get(
    "",
    description="Проверка соединения с базой данных",
)
async def check_db_connection(
    session: AsyncSession = Depends(db_async_session),
) -> None:

    await session.execute(text("select 1"))
