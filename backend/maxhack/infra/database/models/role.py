from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import RoleId
from maxhack.core.role.ids import CREATOR_ROLE_NAME, EDITOR_ROLE_NAME, MEMBER_ROLE_NAME
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel

ROLE_NAME_LEN = 16


class RoleModel(BaseAlchemyModel, IdMixin[RoleId]):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(ROLE_NAME_LEN),
        nullable=False,
        unique=True,
    )

    @property
    def emoji(self) -> str:
        if self.name == CREATOR_ROLE_NAME:
            return "👑"
        if self.name == EDITOR_ROLE_NAME:
            return "🧑‍💻"
        if self.name == MEMBER_ROLE_NAME:
            return "👷‍♂️"
        return ""
