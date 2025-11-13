from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import GroupId, TagId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel

TAG_NAME_LEN = 32
TAG_DESCRIPTION_LEN = 128


class TagModel(BaseAlchemyModel, IdMixin[TagId]):
    __tablename__ = "tags"

    group_id: Mapped[GroupId] = mapped_column(ForeignKey("groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(TAG_NAME_LEN), nullable=False)
    description: Mapped[str] = mapped_column(String(TAG_DESCRIPTION_LEN), nullable=True)
    color: Mapped[str] = mapped_column(String(8), nullable=False)
