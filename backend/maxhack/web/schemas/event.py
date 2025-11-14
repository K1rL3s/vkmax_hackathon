from datetime import datetime
from typing import Literal

from pydantic import Field

from .core import Model
from .group import GroupResponse
from .tag import TagResponse
from maxhack.core.ids import EventId, GroupId, RespondId, TagId, UserId


class CronSchema(Model):
    date: datetime
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
    duration: int = Field(default=0)
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
    duration: int | None = None


class RespondResponse(Model):
    id: RespondId
    status: str


class EventNotifyResponse(Model):
    minutes_before: int


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
    duration: int = 0
    event_happened: bool = False
    respond: RespondResponse | None = None
    notifies: list[int] = Field(default_factory=list)


class EventDetailsResponse(Model):
    id: EventId
    title: str
    description: str | None = None
    cron: str
    is_cycle: bool
    type: Literal["event", "message"]
    creator_id: UserId
    group: GroupResponse
    tags: list[TagResponse]
    notifies: list[EventNotifyResponse]
    timezone: int
    duration: int = 0
    event_happened: bool = False


class EventAddTagRequest(Model):
    tag_ids: list[TagId]


class EventAddUserRequest(Model):
    user_ids: list[UserId]


class EventsResponse(Model):
    events: list[EventResponse]
