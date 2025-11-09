from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import TagId, UserId
from maxhack.infra.database.models.base import BaseAlchemyModel


class UsersToTagsModel(BaseAlchemyModel):
    __tablename__ = "users_to_tags"

    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        primary_key=True,
    )
    tag_id: Mapped[TagId] = mapped_column(
        ForeignKey("tags.id"),
        nullable=False,
        primary_key=True,
    )
