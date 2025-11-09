from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import EventId, TagId
from maxhack.infra.database.models.base import BaseAlchemyModel


class TagsToEvents(BaseAlchemyModel):
    __tablename__ = "tags_to_events"

    tag_id: Mapped[TagId] = mapped_column(
        ForeignKey("tags.id"),
        nullable=False,
        primary_key=True,
    )
    event_id: Mapped[EventId] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        primary_key=True,
    )
