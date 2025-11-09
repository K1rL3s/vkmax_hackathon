from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import GroupId, TagId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel


class TagModel(BaseAlchemyModel, IdMixin[TagId]):
    __tablename__ = "tags"

    group_id: Mapped[GroupId] = mapped_column(ForeignKey("groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    descriptions: Mapped[str] = mapped_column(String(128), nullable=True)
    color: Mapped[str] = mapped_column(String(8), nullable=False)
