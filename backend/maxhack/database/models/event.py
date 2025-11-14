from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maxhack.core.ids import EventId, GroupId, UserId
from maxhack.database.models._mixins import IdMixin
from maxhack.database.models.base import BaseAlchemyModel
from maxhack.database.models.event_notify import EventNotifyModel
from maxhack.database.models.group import GroupModel
from maxhack.database.models.tags_to_events import TagsToEvents

EVENT_TITLE_LEN = 128
EVENT_DESCRIPTION_LEN = 1024


class EventModel(BaseAlchemyModel, IdMixin[EventId]):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(EVENT_TITLE_LEN), nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(EVENT_DESCRIPTION_LEN),
        nullable=True,
    )
    cron: Mapped[str] = mapped_column(String(16), nullable=False)
    is_cycle: Mapped[bool] = mapped_column(Boolean, nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    creator_id: Mapped[UserId] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[GroupId] = mapped_column(ForeignKey("groups.id"), nullable=False)
    timezone: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    event_happened: Mapped[bool] = mapped_column(Boolean, default=False)

    notifies: Mapped[list[EventNotifyModel]] = relationship()
    tags: Mapped[list[TagsToEvents]] = relationship()
    group: Mapped[list[GroupModel]] = relationship()
