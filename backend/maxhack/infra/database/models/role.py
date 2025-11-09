from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from maxhack.core.ids import RoleId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel


class RoleModel(BaseAlchemyModel, IdMixin[RoleId]):
    __tablename__ = "roles"

    name: Mapped[str] = Column(String(16), nullable=False, unique=True)
