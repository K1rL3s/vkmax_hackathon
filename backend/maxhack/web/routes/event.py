from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.event.models import Cron, EventCreate, EventUpdate
from maxhack.core.event.service import EventService
from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import EventId, GroupId
from maxhack.web.dependencies import CurrentUser
from maxhack.web.schemas.event import (
    EventAddTagRequest,
    EventAddUserRequest,
    EventCreateRequest,
    EventResponse,
    EventUpdateRequest,
    EventsResponse,
)

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
    try:
        event, notifies = await event_service.create_event(
            EventCreate(
                **body.model_dump(exclude={"cron"}),
                cron=Cron(**body.cron.model_dump()),
                creator_id=current_user.db_user.id,
            ),
        )
        return await EventResponse.from_orm_async(event, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
    try:
        await event_service.add_tag_to_event(
            event_id=event_id,
            tag_ids=body.tag_ids,
            user_id=current_user.db_user.id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@event_router.get(
    "/{event_id}",
    description="Получить событие. Могут только участники события.",
)
async def get_event_route(
    event_id: EventId,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
) -> EventResponse:
    try:
        event = await event_service.get_event(
            event_id=event_id,
            user_id=current_user.db_user.id,
        )
        return await EventResponse.from_orm_async(event, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
    try:
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
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
    # TODO: Удаление всех связанных сущностей
    try:
        await event_service.delete_event(
            event_id=event_id,
            user_id=current_user.db_user.id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
    try:
        await event_service.add_user_to_event(
            event_id=event_id,
            target_user_ids=body.user_ids,
            user_id=current_user.db_user.id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@event_router.get(
    "/groups/{group_id}",
    description="Просмотр всех событий группы, в которых пользователь принимает участие",
)
async def get_group_events_route(
    group_id: GroupId,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
) -> EventsResponse:
    # TODO: Только возврат событий, в которых участвует юзер
    try:
        events = await event_service.get_group_events(
            group_id=group_id,
            user_id=current_user.db_user.id,
        )
        response_events = [
            await EventResponse.from_orm_async(event, session) for event in events
        ]
        return EventsResponse(events=response_events)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@event_router.get(
    "/",
    description="Просмотр всех своих событий во всех группах.",
)
async def get_user_events_route(
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    current_user: CurrentUser,
) -> EventsResponse:
    try:
        events = await event_service.get_user_events(user_id=current_user.db_user.id)
        response_events = [
            await EventResponse.from_orm_async(event, session) for event in events
        ]
        return EventsResponse(events=response_events)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# @event_router.get(
#     "/users/{slave_id}/events",
#     response_model=EventsResponse,
#     description="Просмотр событий другого пользователя (Если вы в одной группе)",
# )
# async def get_other_user_events_route(
#     slave_id: UserId,
#     event_service: FromDishka[EventService],
#     session: FromDishka[AsyncSession],
#     current_user: CurrentUser,
# ) -> EventsResponse:
#     try:
#         events = await event_service.get_other_user_events(
#             target_user_id=slave_id,
#             user_id=current_user.db_user.id,
#         )
#         response_events = [
#             await EventResponse.from_orm_async(event, session) for event in events
#         ]
#         return EventsResponse(events=response_events)
#     except EntityNotFound as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
#     except NotEnoughRights as e:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
