from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import EventId, EventNotifyId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel


class EventNotifyModel(BaseAlchemyModel, IdMixin[EventNotifyId]):
    __tablename__ = "events_notifies"

    event_id: Mapped[EventId] = mapped_column(ForeignKey("events.id"), nullable=False)
    minutes_before: Mapped[int] = mapped_column(Integer, nullable=False)
