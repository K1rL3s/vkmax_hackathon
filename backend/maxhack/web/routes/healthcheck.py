from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

healthcheck_router = APIRouter(
    prefix="/healthcheck",
    tags=["Healthcheck"],
    route_class=DishkaRoute,
)



@healthcheck_router.get(
    "",
    description="Проверка соединения",
)
async def check_connection(
    session: FromDishka[AsyncSession],
) -> None:
    await session.execute(text("select 1"))
