from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.ids import MaxChatId, MaxId, UserId
from maxhack.infra.database.models._mixins import IdMixin
from maxhack.infra.database.models.base import BaseAlchemyModel

USER_FIRST_NAME_LEN = 64
USER_LAST_NAME_LEN = 64
USER_PHONE_LEN = 16


class UserModel(BaseAlchemyModel, IdMixin[UserId]):
    __tablename__ = "users"

    max_id: Mapped[MaxId] = mapped_column(Integer, nullable=False, unique=True)
    max_chat_id: Mapped[MaxChatId] = mapped_column(Integer, nullable=False, unique=True)
    max_photo: Mapped[str] = mapped_column(String(256), nullable=True)
    first_name: Mapped[str] = mapped_column(String(USER_FIRST_NAME_LEN), nullable=False)
    last_name: Mapped[str | None] = mapped_column(
        String(USER_LAST_NAME_LEN),
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(String(USER_PHONE_LEN), nullable=True)
    timezone: Mapped[int] = mapped_column(Integer, nullable=False)
    notify_mode: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=NotifyMode.DEFAULT,
    )
