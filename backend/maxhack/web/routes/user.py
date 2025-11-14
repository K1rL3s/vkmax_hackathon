from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.event.service import EventService
from maxhack.core.ids import GroupId, MaxChatId, MaxId, TagId, UserId
from maxhack.core.tag.service import TagService
from maxhack.core.user.service import UserService
from maxhack.web.dependencies import CurrentUser
from maxhack.web.schemas.event import EventResponse
from maxhack.web.schemas.tag import TagResponse
from maxhack.web.schemas.user import (
    PersonalGroupResponse,
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
    user = await user_service.create_user(
        max_id=MaxId(body.max_id),
        max_chat_id=MaxChatId(body.max_chat_id),
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        timezone=body.timezone,
    )
    return await UserResponse.from_orm_async(user, session)


@user_router.get(
    "/me",
    description="Получить пользователя. Можно только самого себя.",
)
async def get_user_by_id_route(
    current_user: CurrentUser,
    user_service: FromDishka[UserService],
    session: FromDishka[AsyncSession],
) -> UserResponse:
    user = await user_service.get_user_by_max_id(
        max_id=MaxId(current_user.db_user.max_id),
    )
    return await UserResponse.from_orm_async(user, session)


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
    user = await user_service.update_user(
        user_id=current_user.db_user.id,
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        timezone=body.timezone,
        notify_mode=body.notify_mode,
    )
    return await UserResponse.from_orm_async(user, session)


@user_router.get(
    "/me/groups/personal",
    description="Получить персональную группу пользователя.",
)
async def get_personal_group_route(
    user_service: FromDishka[UserService],
    current_user: CurrentUser,
) -> PersonalGroupResponse:
    personal_group = await user_service.get_personal_group(
        user_id=UserId(current_user.db_user.id),
    )
    return PersonalGroupResponse.model_validate(personal_group)


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


@user_router.get("/me/events")
async def list_personal_events_route(
    user_service: FromDishka[UserService],
    current_user: CurrentUser,
    tag_ids: str | None = Query(
        None,
        description="Список ID тегов через запятую для фильтрации",
    ),
) -> list[EventResponse]:
    """
    Получение личных событий пользователя
    """
    parsed_tag_ids: list[TagId] | None = None
    if tag_ids:
        parsed_tag_ids = [TagId(int(tid.strip())) for tid in tag_ids.split(",") if tid.strip()]

    events = await user_service.get_personal_events(
        user_id=UserId(current_user.db_user.id),
        tag_ids=parsed_tag_ids,
    )
    response_events = []
    for event in events:
        event_dict = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "cron": event.cron,
            "is_cycle": event.is_cycle,
            "type": event.type,
            "creator_id": event.creator_id,
            "group_id": event.group_id,
            "timezone": event.timezone,
            "duration": event.duration,
            "event_happened": event.event_happened,
            "notifies": [notify.minutes_before for notify in event.notifies],
        }
        response_events.append(EventResponse.model_validate(event_dict))
    return response_events


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
    tags = await tag_service.list_user_tags(
        group_id=group_id,
        user_id=user_id,
        master_id=current_user.db_user.id,
    )
    response_tags = [await TagResponse.from_orm_async(tag, session) for tag in tags]
    return response_tags


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
        description="Список ID тегов через запятую для фильтрации",
    ),
) -> list[EventResponse]:
    parsed_tag_ids: list[TagId] | None = None
    if tag_ids:
        parsed_tag_ids = [TagId(int(tid.strip())) for tid in tag_ids.split(",") if tid.strip()]

    events = await event_service.list_user_events(
        group_id=group_id,
        user_id=user_id,
        master_id=current_user.db_user.id,
        tag_ids=parsed_tag_ids,
    )
    response_events = []
    for event in events:
        event_dict = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "cron": event.cron,
            "is_cycle": event.is_cycle,
            "type": event.type,
            "creator_id": event.creator_id,
            "group_id": event.group_id,
            "timezone": event.timezone,
            "duration": event.duration,
            "event_happened": event.event_happened,
            "notifies": [notify.minutes_before for notify in event.notifies],
        }
        response_events.append(EventResponse.model_validate(event_dict))
    return response_events
