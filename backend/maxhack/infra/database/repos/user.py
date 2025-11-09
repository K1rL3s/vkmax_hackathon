from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.exceptions import MaxHackError
from maxhack.core.ids import MaxChatId, MaxId, UserId
from maxhack.infra.database.models import GroupModel, UserModel, UsersToGroupsModel
from maxhack.infra.database.repos.base import BaseAlchemyRepo


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
        first_name: str | None,
        last_name: str | None,
        phone: str | None,
    ) -> UserModel:
        user = UserModel(
            max_id=max_id,
            max_chat_id=max_chat_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        try:
            self._session.add(user)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            # ошибка если дубликат id, max_id итп
            raise MaxHackError from e  # TODO: Заменить на ошибку из БЛ

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

    async def get_user_groups(
        self,
        user_id: UserId,
    ) -> list[tuple[UsersToGroupsModel, GroupModel]]:
        pass
        # stmt = (
        #     select(UsersToGroupsModel, GroupModel)
        #     .join(GroupModel, UsersToGroupsModel.group_id == GroupModel.id)
        #     .where(UsersToGroupsModel.user_id == user_id)
        # )
        #
        # result = await self._session.execute(stmt)
        # return result.all()
