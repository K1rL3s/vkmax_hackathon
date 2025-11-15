from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import EventId, UserId
from maxhack.database.models._mixins import IdMixin
from maxhack.database.models.base import BaseAlchemyModel


class UsersToEvents(BaseAlchemyModel, IdMixin[int]):
    __tablename__ = "users_to_events"
    __table_args__ = (
        Index(
            None,
            "user_id",
            "event_id",
            unique=True,
            postgresql_where="users_to_events.deleted_at IS NULL",
        ),
    )

    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    event_id: Mapped[EventId] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
    )
