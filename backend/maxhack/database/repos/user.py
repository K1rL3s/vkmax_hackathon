from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.exceptions import InvalidValue
from maxhack.core.ids import MaxChatId, MaxId, UserId
from maxhack.database.models import UserModel
from maxhack.database.repos.base import BaseAlchemyRepo


class UserRepo(BaseAlchemyRepo):
    async def get_by_id(self, user_id: UserId) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        return await self._session.scalar(stmt)

    async def get_by_max_id(self, max_id: MaxId) -> UserModel:
        stmt = select(UserModel).where(UserModel.max_id == max_id)
        return await self._session.scalar(stmt)

    async def create_user(
        self,
        max_id: MaxId,
        max_chat_id: MaxChatId,
        first_name: str,
        last_name: str | None,
        phone: str | None,
        timezone: int = 0,
    ) -> UserModel:
        user = UserModel(
            max_id=max_id,
            max_chat_id=max_chat_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            timezone=timezone,
        )
        try:
            self._session.add(user)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            # ошибка если дубликат id, max_id итп
            raise InvalidValue from e

        return user

    async def update_user(self, user_id: UserId, **values: Any) -> UserModel | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        for field_name, field_value in values.items():
            setattr(user, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(user)

        return user
