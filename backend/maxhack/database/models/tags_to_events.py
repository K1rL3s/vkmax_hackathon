from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maxhack.core.ids import EventId, TagId
from maxhack.database.models._mixins import IdMixin
from maxhack.database.models.base import BaseAlchemyModel
from maxhack.database.models.tag import TagModel


class TagsToEvents(BaseAlchemyModel, IdMixin[int]):
    __tablename__ = "tags_to_events"
    __table_args__ = (
        Index(
            None,
            "tag_id",
            "event_id",
            unique=True,
            postgresql_where="tags_to_events.deleted_at IS NULL",
        ),
    )

    tag_id: Mapped[TagId] = mapped_column(
        ForeignKey("tags.id"),
        nullable=False,
    )
    event_id: Mapped[EventId] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
    )

    tag: Mapped[TagModel] = relationship()
