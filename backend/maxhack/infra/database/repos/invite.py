from typing import Any

from sqlalchemy import select, update

from maxhack.core.ids import GroupId, InviteId, InviteKey, UserId
from maxhack.infra.database.models import InviteModel
from maxhack.infra.database.repos.base import BaseAlchemyRepo


class InviteRepo(BaseAlchemyRepo):
    async def create(
        self,
        key: InviteKey,
        group_id: GroupId,
        creator_id: UserId,
    ) -> InviteModel:
        invite = InviteModel(
            key=key,
            group_id=group_id,
            creator_id=creator_id,
        )
        self._session.add(invite)
        await self._session.flush()
        return invite

    async def update(self, invite_id: InviteId, **values: Any) -> InviteModel | None:
        stmt = (
            update(InviteModel)
            .where(InviteModel.id == invite_id)
            .values(**values)
            .returning(InviteModel)
        )
        invite = await self._session.scalar(stmt)
        await self._session.flush()
        return invite

    async def get_by_id(self, invite_id: InviteId) -> InviteModel | None:
        stmt = select(InviteModel).where(InviteModel.id == invite_id)
        return await self._session.scalar(stmt)

    async def get_by_key(self, invite_key: InviteKey) -> InviteModel | None:
        stmt = select(InviteModel).where(InviteModel.key == invite_key)
        return await self._session.scalar(stmt)

    async def get_group_invite(self, group_id: GroupId) -> InviteModel | None:
        stmt = (
            select(InviteModel)
            .where(InviteModel.group_id == group_id, InviteModel.is_not_deleted)
            .limit(1)
        )
        return await self._session.scalar(stmt)
