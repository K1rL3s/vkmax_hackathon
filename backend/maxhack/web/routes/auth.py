from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Query
from starlette import status

from maxo.utils.webapp import WebAppInitData

from maxhack.config import MaxConfig
from maxhack.web.dependencies import validate_web_app_data

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    route_class=DishkaRoute,
)


@auth_router.get(
    "",
    description="Валидация WebAppData из MAX",
)
async def check_init_data(
    *,
    response: Response,
    web_app_data: str = Query(alias="WebAppData"),
    max_config: FromDishka[MaxConfig],
) -> WebAppInitData:
    try:
        data = validate_web_app_data(max_config.token, web_app_data)
        response.set_cookie("WebAppData", web_app_data)
        return data
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Невалидная WebAppData",
        )
