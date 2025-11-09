from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import GroupId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel


class GroupModel(BaseAlchemyModel, IdMixin[GroupId]):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(128), nullable=True)
