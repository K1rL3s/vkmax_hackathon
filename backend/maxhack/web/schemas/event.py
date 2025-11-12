from datetime import datetime
from typing import Literal

from pydantic import Field

from maxhack.core.enums.respond_action import RespondStatus
from maxhack.core.ids import EventId, GroupId, RespondId, TagId, UserId

from .core import Model


class CronSchema(Model):
    date: datetime | None = None
    every_day: bool = False
    every_week: bool = False
    every_month: bool = False


class EventCreateRequest(Model):
    title: str
    description: str | None = None
    timezone: int | None = None
    type: Literal["event"] = Field("event", description="Тип события")
    cron: CronSchema
    group_id: GroupId
    participants_ids: list[UserId] = Field(
        default_factory=list[UserId],
        description="Упомянаемые пользователи",
    )
    tags_ids: list[TagId] = Field(
        default_factory=list[TagId],
        description="Привязанные теги",
    )
    minutes_before: list[int] = Field(default_factory=list)


class EventUpdateRequest(Model):
    title: str | None = None
    description: str | None = None
    type: str | None = None
    timezone: int | None = None
    cron: CronSchema | None = None


class EventResponse(Model):
    id: EventId
    title: str
    description: str | None = None
    cron: str
    is_cycle: bool
    type: str
    creator_id: UserId
    group_id: GroupId
    timezone: int
    # todo: сделать возврат notifies
    # notifies: list[int]


class EventAddTagRequest(Model):
    tag_ids: list[TagId]


class EventAddUserRequest(Model):
    user_ids: list[UserId]


class EventsResponse(Model):
    events: list[EventResponse]


class RespondChangeResponse(Model):
    status: RespondStatus


class RespondResponse(Model):
    id: RespondId
    user_id: UserId
    event_id: EventId
    status: str
