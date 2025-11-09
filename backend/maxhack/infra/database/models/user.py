from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.ids import MaxChatId, MaxId, UserId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel


class UserModel(BaseAlchemyModel, IdMixin[UserId]):
    __tablename__ = "users"
    # __table_args__ = (UniqueConstraint("username", postgresql_nulls_not_distinct=True),)

    max_id: Mapped[MaxId] = mapped_column(Integer, nullable=False, unique=True)
    max_chat_id: Mapped[MaxChatId] = mapped_column(Integer, nullable=False, unique=True)
    # username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(16), nullable=True)
