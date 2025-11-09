from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import EventId, GroupId, UserId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel


class EventModel(BaseAlchemyModel, IdMixin[EventId]):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(128), nullable=True)
    cron: Mapped[str] = mapped_column(String(64), nullable=False)
    is_cycle: Mapped[bool] = mapped_column(Boolean, nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    creator_id: Mapped[UserId] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[GroupId | None] = mapped_column(
        ForeignKey("groups.id"),
        nullable=True,
    )
