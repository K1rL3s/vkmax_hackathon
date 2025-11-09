from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import EventId, RespondId, UserId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel


class RespondModel(BaseAlchemyModel, IdMixin[RespondId]):
    __tablename__ = "responds"

    user_id: Mapped[UserId] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[EventId] = mapped_column(ForeignKey("events.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
