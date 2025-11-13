from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.ids import GroupId, InviteId, RoleId, UserId
from maxhack.infra.database.models import UserModel
from maxhack.infra.database.models.base import BaseAlchemyModel
from maxhack.infra.database.models.role import RoleModel


class UsersToGroupsModel(BaseAlchemyModel):
    __tablename__ = "users_to_groups"

    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        primary_key=True,
    )
    group_id: Mapped[GroupId] = mapped_column(
        ForeignKey("groups.id"),
        nullable=False,
        primary_key=True,
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
