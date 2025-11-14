from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.event.models import Cron, EventCreate, EventUpdate
from maxhack.core.event.service import EventService
from maxhack.core.ids import EventId, GroupId, UserId
from maxhack.web.dependencies import CurrentUser
from maxhack.web.utils.ics import generate_ics_for_events
from maxhack.web.schemas.event import (
    EventAddTagRequest,
    EventAddUserRequest,
    EventCreateRequest,
    EventDetailsResponse,
    EventNotifyResponse,
    EventResponse,
    EventUpdateRequest,
    EventsResponse,
    RespondResponse,
)
from maxhack.web.schemas.group import GroupResponse
from maxhack.web.schemas.tag import TagResponse

event_router = APIRouter(
    prefix="/events",
    tags=["Events"],
    route_class=DishkaRoute,
)


@event_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="""
Создать событие (встреча или сообщение) в группе.
Могут только "Босс" и "Начальник".
""".strip(),
)
async def create_event_route(
    body: EventCreateRequest,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
) -> EventResponse:
    event, notifies = await event_service.create_event(
        EventCreate(
            **body.model_dump(exclude={"cron"}),
            cron=Cron(**body.cron.model_dump()),
            creator_id=current_user.db_user.id,
        ),
    )
    return await EventResponse.from_orm_async(event, session)


@event_router.post(
    "/{event_id}/tags",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""Добавить тег для события. Могут только "Босс" и "Начальник".""",
)
async def add_tag_to_event_route(
    event_id: EventId,
    body: EventAddTagRequest,
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> None:
    await event_service.add_tag_to_event(
        event_id=event_id,
        tag_ids=body.tag_ids,
        user_id=current_user.db_user.id,
    )


@event_router.get(
    "/{event_id}",
    description="Получить событие. Могут только участники события.",
)
async def get_event_route(
    event_id: EventId,
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> EventDetailsResponse:
    event = await event_service.get_event(
        event_id=event_id,
        user_id=UserId(current_user.db_user.id),
    )
    return EventDetailsResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        cron=event.cron,
        is_cycle=event.is_cycle,
        type=event.type,  # type: ignore  # noqa: PGH003
        creator_id=event.creator_id,
        group=GroupResponse.model_validate(event.group),
        tags=[
            TagResponse.model_validate(tag_to_event.tag) for tag_to_event in event.tags
        ],
        notifies=[
            EventNotifyResponse.model_validate(notify) for notify in event.notifies
        ],
        timezone=event.timezone,
        duration=event.duration,
        event_happened=event.event_happened,
    )


@event_router.patch(
    "/{event_id}",
    description="""Редактировать событие. Могут только "Босс" и "Начальник".""",
)
async def update_event_route(
    event_id: EventId,
    body: EventUpdateRequest,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
) -> EventResponse:
    event = await event_service.update_event(
        event_id=event_id,
        user_id=current_user.db_user.id,
        event_update_model=EventUpdate(
            **body.model_dump(exclude={"cron"}),
            cron=(
                Cron(
                    **body.cron.model_dump(),
                )
                if body.cron
                else None
            ),
        ),
    )
    return await EventResponse.from_orm_async(event, session)


@event_router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""Удалить событие. Могут только "Босс" и "Начальник".""",
)
async def delete_event_route(
    event_id: EventId,
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> None:
    await event_service.delete_event(
        event_id=event_id,
        user_id=current_user.db_user.id,
    )


@event_router.post(
    "/{event_id}/users",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""
Добавить (привязать) пользователя в событие.
Могут только "Босс" и "Начальник".
""".strip(),
)
async def add_user_to_event_route(
    event_id: EventId,
    body: EventAddUserRequest,
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> None:
    await event_service.add_user_to_event(
        event_id=event_id,
        target_user_ids=body.user_ids,
        user_id=current_user.db_user.id,
    )


@event_router.get(
    "/groups/{group_id}",
    description="Просмотр всех событий группы, в которых пользователь принимает участие",
)
async def get_group_events_route(
    group_id: GroupId,
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> EventsResponse:
    events_with_responds = await event_service.get_group_events(
        group_id=group_id,
        user_id=UserId(current_user.db_user.id),
    )
    response_events = []
    for event, respond in events_with_responds:
        # Создаем EventResponse вручную, исключая notifies из автоматической конвертации
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
        if respond is not None:
            event_dict["respond"] = {
                "id": respond.id,
                "status": respond.status,
            }
        event_response = EventResponse.model_validate(event_dict)
        response_events.append(event_response)
    return EventsResponse(events=response_events)


@event_router.get(
    "/",
    description="Просмотр всех своих событий во всех группах.",
)
async def get_user_events_route(
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> EventsResponse:
    events = await event_service.get_user_events(
        user_id=UserId(current_user.db_user.id),
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
    return EventsResponse(events=response_events)


@event_router.get(
    "/export/all-groups",
    description="Выгрузить все события группы, в которых участвует пользователь, во всех группах",
    response_class=Response,
)
async def export_user_events_all_groups_route(
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> Response:
    """Выгружает все события, в которых участвует пользователь, из всех его групп."""
    user_id = UserId(current_user.db_user.id)

    events, groups_dict = await event_service.get_user_events_all_groups_for_export(user_id)

    # Генерируем .ics файл
    ics_content = generate_ics_for_events(events, groups_dict)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": 'attachment; filename="events_all_groups.ics"',
        },
    )


@event_router.get(
    "/export/groups/{group_id}/user",
    description="Выгрузить все события пользователя в рамках одной группы",
    response_class=Response,
)
async def export_user_events_in_group_route(
    group_id: GroupId,
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> Response:
    """Выгружает все события пользователя в рамках одной группы."""
    user_id = UserId(current_user.db_user.id)

    events, groups_dict = await event_service.get_user_events_in_group_for_export(
        group_id=group_id,
        user_id=user_id,
    )

    # Генерируем .ics файл
    ics_content = generate_ics_for_events(events, groups_dict)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="events_group_{group_id}.ics"',
        },
    )


@event_router.get(
    "/export/groups/{group_id}/all",
    description="Выгрузить все события группы (только для ролей 1 и 2)",
    response_class=Response,
)
async def export_all_group_events_route(
    group_id: GroupId,
    event_service: FromDishka[EventService],
    current_user: CurrentUser,
) -> Response:
    """Выгружает все события группы. Доступно только для ролей 1 (CREATOR) и 2 (EDITOR)."""
    user_id = UserId(current_user.db_user.id)

    events, groups_dict = await event_service.get_all_group_events_for_export(
        group_id=group_id,
        user_id=user_id,
    )

    # Генерируем .ics файл
    ics_content = generate_ics_for_events(events, groups_dict)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="all_events_group_{group_id}.ics"',
        },
    )
