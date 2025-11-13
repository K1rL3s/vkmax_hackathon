from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.event.service import EventService
from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import GroupId, MaxChatId, MaxId, UserId
from maxhack.core.tag.service import TagService
from maxhack.core.user.service import UserService
from maxhack.web.dependencies import CurrentUser
from maxhack.web.schemas.event import EventResponse
from maxhack.web.schemas.tag import TagResponse
from maxhack.web.schemas.user import (
    UserCreateRequest,
    UserGroupItem,
    UserGroupsResponse,
    UserResponse,
    UserUpdateRequest,
)

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    route_class=DishkaRoute,
)


# TODO: Удалить на проде
@user_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Создание пользователя",
)
async def create_user_route(
    body: UserCreateRequest,
    user_service: FromDishka[UserService],
    session: FromDishka[AsyncSession],
) -> UserResponse:
    try:
        user = await user_service.create_user(
            max_id=MaxId(body.max_id),
            max_chat_id=MaxChatId(body.max_chat_id),
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
            timezone=body.timezone,
        )
        return await UserResponse.from_orm_async(user, session)
    except InvalidValue as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@user_router.get(
    "/me",
    description="Получить пользователя. Можно только самого себя.",
)
async def get_user_by_id_route(
    current_user: CurrentUser,
    user_service: FromDishka[UserService],
    session: FromDishka[AsyncSession],
) -> UserResponse:
    try:
        user = await user_service.get_user_by_max_id(
            max_id=MaxId(current_user.db_user.id),
        )
        return await UserResponse.from_orm_async(user, session)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@user_router.patch(
    "/",
    description="Редактировать пользователя. Можно только самого себя.",
)
async def update_user_route(
    body: UserUpdateRequest,
    user_service: FromDishka[UserService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
) -> UserResponse:
    try:
        user = await user_service.update_user(
            user_id=current_user.db_user.id,
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
        )
        return await UserResponse.from_orm_async(user, session)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@user_router.get(
    "/me/groups",
    description="""
Получить список групп, в которых состоит пользователь. Можно только свои группы.
""".strip(),
)
async def list_user_groups_route(
    user_service: FromDishka[UserService],
    current_user: CurrentUser,
) -> UserGroupsResponse:
    try:
        result = await user_service.get_user_groups(
            user_id=current_user.db_user.id,
            master_id=current_user.db_user.id,
        )
        items: list[UserGroupItem] = []
        for group, role in result:
            items.append(
                UserGroupItem(
                    group_id=group.id,
                    name=group.name,
                    description=group.description,
                    role_id=role.id,
                ),
            )

        return UserGroupsResponse(groups=items)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@user_router.get(
    "/{user_id}/groups/{group_id}/tags",
    description="Получить список тегов пользователя в рамках группы",
)
async def list_user_tags_route(
    user_id: UserId,
    group_id: GroupId,
    tag_service: FromDishka[TagService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
) -> list[TagResponse]:
    try:
        tags = await tag_service.list_user_tags(
            group_id=group_id,
            user_id=user_id,
            master_id=current_user.db_user.id,
        )
        response_tags = [await TagResponse.from_orm_async(tag, session) for tag in tags]
        return response_tags
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@user_router.get(
    "/{user_id}/groups/{group_id}/events",
    description="Получить список событий пользователя в рамках группы",
)
async def list_user_events_route(
    user_id: UserId,
    group_id: GroupId,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
    tag_ids: str | None = Query(
            None,
            description="Список ID тегов через запятую для фильтрации"
        ),
) -> list[EventResponse]:
    try:
        events = await event_service.list_user_events(
            group_id=group_id,
            user_id=user_id,
            master_id=current_user.db_user.id,
            tag_ids=tag_ids
        )
        response_events = [
            await EventResponse.from_orm_async(event, session) for event in events
        ]
        return response_events
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
