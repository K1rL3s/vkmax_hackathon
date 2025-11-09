from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.exceptions import MaxHackError
from maxhack.core.ids import GroupId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID
from maxhack.infra.database.models import GroupModel, UsersToGroupsModel
from maxhack.infra.database.repos.base import BaseAlchemyRepo


class GroupRepo(BaseAlchemyRepo):
    async def get_by_id(self, group_id: GroupId) -> GroupModel | None:
        stmt = select(GroupModel).where(GroupModel.id == group_id)
        return await self._session.scalar(stmt)

    async def create(
        self,
        name: str,
        description: str | None,
        creator_id: UserId,
    ) -> GroupModel:
        group = GroupModel(name=name, description=description)
        try:
            self._session.add(group)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise MaxHackError from e  # TODO: Заменить на ошибку из БЛ

        role = UsersToGroupsModel(
            user_id=creator_id,
            group_id=group.id,
            role_id=CREATOR_ROLE_ID,
            invite_id=None,
        )
        try:
            self._session.add(role)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise MaxHackError from e  # TODO: Заменить на ошибку из БЛ

        return group

    async def update(self, group_id: GroupId, **values: Any) -> GroupModel | None:
        stmt = (
            update(GroupModel)
            .where(GroupModel.id == group_id)
            .values(**values)
            .returning(GroupModel)
        )
        try:
            group = await self._session.scalar(stmt)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise MaxHackError from e  # TODO: Заменить на ошибку из БЛ

        return group
