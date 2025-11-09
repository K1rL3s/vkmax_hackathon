from datetime import datetime

from sqlalchemy import ColumnElement, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column


def fresh_timestamp() -> ColumnElement[datetime]:
    return func.timezone("UTC", func.now())


class IdMixin[T]:
    id: Mapped[T] = mapped_column(Integer, primary_key=True, autoincrement=True)


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=fresh_timestamp(),
        server_default=fresh_timestamp(),
        nullable=False,
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=fresh_timestamp(),
        default=fresh_timestamp(),
        server_default=fresh_timestamp(),
        server_onupdate=fresh_timestamp(),
        nullable=False,
    )


class DeletedAtMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=None,
        server_onupdate=None,
        nullable=True,
    )
