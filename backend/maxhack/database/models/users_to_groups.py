from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.ids import GroupId, InviteId, RoleId, UserId
from maxhack.database.models import UserModel
from maxhack.database.models._mixins import IdMixin
from maxhack.database.models.base import BaseAlchemyModel
from maxhack.database.models.role import RoleModel


class UsersToGroupsModel(BaseAlchemyModel, IdMixin[int]):
    __tablename__ = "users_to_groups"
    __table_args__ = (
        Index(
            None,
            "user_id",
            "group_id",
            unique=True,
            postgresql_where="users_to_groups.deleted_at IS NULL",
        ),
    )

    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    group_id: Mapped[GroupId] = mapped_column(
        ForeignKey("groups.id"),
        nullable=False,
    )
    role_id: Mapped[RoleId] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )
    invite_id: Mapped[InviteId | None] = mapped_column(
        ForeignKey("invites.id"),
        nullable=True,
    )
    notify_mode: Mapped[NotifyMode] = mapped_column(
        String(16),
        nullable=False,
        default=NotifyMode.DEFAULT,
    )

    user: Mapped[UserModel] = relationship()
    role: Mapped[RoleModel] = relationship()
