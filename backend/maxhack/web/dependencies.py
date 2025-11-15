import urllib.parse
from dataclasses import dataclass
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException
from fastapi.params import Header
from starlette import status

from maxo.utils.webapp import (
    WebAppChat,
    WebAppInitData,
    WebAppUser,
    safe_parse_webapp_init_data,
)

from maxhack.config import MaxConfig
from maxhack.core.exceptions import UserNotFound
from maxhack.core.ids import MaxChatId, MaxId
from maxhack.core.user.service import UserService
from maxhack.web.schemas.user import UserResponse


@dataclass(slots=True, frozen=True, kw_only=True)
class _CurrentUserData:
    ip: str | None = None
    query_id: str | None = None
    auth_date: str | None = None
    hash: str
    chat: WebAppChat
    max_user: WebAppUser
    db_user: UserResponse


def validate_web_app_data(token: str, web_app_data: str) -> WebAppInitData:
    try:
        return safe_parse_webapp_init_data(token, web_app_data)
    except ValueError:
        web_app_data = urllib.parse.unquote(web_app_data)
        return safe_parse_webapp_init_data(token, web_app_data)


@inject
async def get_current_user(
    *,
    web_app_data: str = Header(alias="WebAppData"),
    max_config: FromDishka[MaxConfig],
    user_service: FromDishka[UserService],
) -> _CurrentUserData:
    try:
        webapp = validate_web_app_data(max_config.token, web_app_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидная WebAppData",
        )

    try:
        user = await user_service.get_user_by_max_id(MaxId(webapp.user.id))
    except UserNotFound:
        user = await user_service.create_user(
            max_id=MaxId(webapp.user.id),
            max_chat_id=MaxChatId(webapp.chat.id),
            first_name=webapp.user.first_name,
            last_name=webapp.user.last_name,
            max_photo=webapp.user.photo_url,
        )

    return _CurrentUserData(
        ip=webapp.ip,
        query_id=webapp.query_id,
        auth_date=webapp.auth_date,
        hash=webapp.hash,
        chat=webapp.chat,
        max_user=webapp.user,
        db_user=user,  # type: ignore
    )


CurrentUser = Annotated[_CurrentUserData, Depends(get_current_user)]
