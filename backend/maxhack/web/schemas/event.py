from ...core.ids import EventId, GroupId, TagId, UserId
from .core import Model


class EventCreateRequest(Model):
    title: str
    description: str | None = None
    cron: str
    is_cycle: bool
    type: str
    group_id: GroupId | None = None


class EventUpdateRequest(Model):
    title: str | None = None
    description: str | None = None
    cron: str | None = None
    is_cycle: bool | None = None
    type: str | None = None


class EventResponse(Model):
    id: EventId
    title: str
    description: str | None = None
    cron: str
    is_cycle: bool
    type: str
    creator_id: UserId
    group_id: GroupId | None = None



class EventAddTagRequest(Model):
    tag_id: TagId


class EventAddUserRequest(Model):
    user_id: UserId


class EventsResponse(Model):
    events: list[EventResponse]
