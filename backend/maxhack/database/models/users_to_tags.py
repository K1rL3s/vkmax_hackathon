from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import TagId, UserId
from maxhack.database.models._mixins import DeletedAtMixin, IdMixin
from maxhack.database.models.base import BaseAlchemyModel


class UsersToTagsModel(BaseAlchemyModel, IdMixin[int], DeletedAtMixin):
    __tablename__ = "users_to_tags"
    __table_args__ = (
        Index(
            None,
            "user_id",
            "tag_id",
            unique=True,
            postgresql_where="users_to_tags.deleted_at IS NULL",
        ),
    )

    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    tag_id: Mapped[TagId] = mapped_column(
        ForeignKey("tags.id"),
        nullable=False,
    )
