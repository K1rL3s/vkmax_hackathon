from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.event.service import EventService
from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import EventId, GroupId, RespondId, UserId
from maxhack.core.responds.service import RespondService
from maxhack.web.schemas.event import (
    EventAddTagRequest,
    EventAddUserRequest,
    EventCreateRequest,
    EventResponse,
    EventUpdateRequest,
    EventsResponse,
    RespondChangeResponse,
    RespondResponse,
)

event_router = APIRouter(prefix="/events", tags=["Events"], route_class=DishkaRoute)


@event_router.post(
    "/{event_id}/tags",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Добавить тег для события (может только 1 и 2 роль)",
)
async def add_tag_to_event_route(
    event_id: EventId,
    body: EventAddTagRequest,
    event_service: FromDishka[EventService],
    master_id: UserId = Header(...),
) -> None:
    try:
        await event_service.add_tag_to_event(
            event_id=event_id,
            tag_ids=body.tag_ids,
            user_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@event_router.get(
    "/{event_id}",
    response_model=EventResponse,
    description="Получить событие",
)
async def get_event_route(
    event_id: EventId,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> EventResponse:
    try:
        event = await event_service.get_event(event_id=event_id, user_id=master_id)
        return await EventResponse.from_orm_async(event, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@event_router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создание события (может только 1 и 2 роль)",
)
async def create_event_route(
    body: EventCreateRequest,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> EventResponse:
    try:
        event = await event_service.create_event(
            title=body.title,
            description=body.description,
            cron=body.cron,
            is_cycle=body.is_cycle,
            type=body.type,
            creator_id=master_id,
            group_id=body.group_id,
        )
        return await EventResponse.from_orm_async(event, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@event_router.patch(
    "/{event_id}",
    response_model=EventResponse,
    description="Редактирование события (может только 1 и 2 роль)",
)
async def update_event_route(
    event_id: EventId,
    body: EventUpdateRequest,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> EventResponse:
    try:
        event = await event_service.update_event(
            event_id=event_id,
            user_id=master_id,
            title=body.title,
            description=body.description,
            cron=body.cron,
            is_cycle=body.is_cycle,
            type=body.type,
        )
        return await EventResponse.from_orm_async(event, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@event_router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление события (может только 1 и 2 роль)",
)
async def delete_event_route(
    event_id: EventId,
    event_service: FromDishka[EventService],
    master_id: UserId = Header(...),
) -> None:
    try:
        await event_service.delete_event(event_id=event_id, user_id=master_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@event_router.post(
    "/{event_id}/users",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Добавить пользователя для события (может только 1 и 2 роль)",
)
async def add_user_to_event_route(
    event_id: EventId,
    body: EventAddUserRequest,
    event_service: FromDishka[EventService],
    master_id: UserId = Header(...),
) -> None:
    try:
        await event_service.add_user_to_event(
            event_id=event_id,
            target_user_id=body.user_ids,
            user_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@event_router.get(
    "/groups/{group_id}",
    response_model=EventsResponse,
    description="Просмотр всех событий группы (может только пользователь находящийся в этой группе)",
)
async def get_group_events_route(
    group_id: GroupId,
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> EventsResponse:
    try:
        events = await event_service.get_group_events(
            group_id=group_id,
            user_id=master_id,
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
    response_model=EventsResponse,
    description="Просмотр всех своих событий",
)
async def get_user_events_route(
    event_service: FromDishka[EventService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> EventsResponse:
    try:
        events = await event_service.get_user_events(user_id=master_id)
        response_events = [
            await EventResponse.from_orm_async(event, session) for event in events
        ]
        return EventsResponse(events=response_events)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@event_router.patch(
    "/respond/{respond_id}/{event_id}",
    response_model=RespondResponse,
    description="Изменить статус отклика",
)
async def get_user_events_route(
    respond_id: RespondId,
    event_id: EventId,
    body: RespondChangeResponse,
    respond_service: FromDishka[RespondService],
    master_id: UserId = Header(...),
) -> RespondResponse:
    try:
        respond = await respond_service.update(
            respond_id,
            event_id,
            master_id,
            status=body.status,
        )
        return RespondResponse.model_validate(respond)
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
#     master_id: UserId = Header(...),
# ) -> EventsResponse:
#     try:
#         events = await event_service.get_other_user_events(
#             target_user_id=slave_id,
#             user_id=master_id,
#         )
#         response_events = [
#             await EventResponse.from_orm_async(event, session) for event in events
#         ]
#         return EventsResponse(events=response_events)
#     except EntityNotFound as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
#     except NotEnoughRights as e:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
