from sqlalchemy import and_, func, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm.strategy_options import joinedload

from maxhack.core.exceptions import MaxHackError
from maxhack.core.ids import GroupId, InviteId, RoleId, UserId
from maxhack.core.role.ids import MEMBER_ROLE_ID
from maxhack.infra.database.models import (
    GroupModel,
    RoleModel,
    UsersToGroupsModel,
)
from maxhack.infra.database.repos.base import BaseAlchemyRepo


class UsersToGroupsRepo(BaseAlchemyRepo):
    async def user_groups(
        self,
        user_id: UserId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[tuple[GroupModel, RoleModel]]:
        stmt = (
            select(GroupModel, RoleModel)
            .join(
                UsersToGroupsModel,
                and_(
                    UsersToGroupsModel.group_id == GroupModel.id,
                    UsersToGroupsModel.user_id == user_id,
                    UsersToGroupsModel.deleted_at.is_(None),
                ),
            )
            .join(
                RoleModel,
                RoleModel.id == UsersToGroupsModel.role_id,
            )
            .order_by(UsersToGroupsModel.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(await self._session.execute(stmt))

    async def group_users(
        self,
        group_id: GroupId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[UsersToGroupsModel]:
        stmt = (
            select(UsersToGroupsModel)
            .join(UsersToGroupsModel.role)
            .options(
                joinedload(UsersToGroupsModel.role),
                joinedload(UsersToGroupsModel.user),
            )
            .where(
                UsersToGroupsModel.group_id == group_id,
                UsersToGroupsModel.deleted_at.is_(None),
            )
            .order_by(
                UsersToGroupsModel.created_at.asc(),
                RoleModel.id.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return list(await self._session.scalars(stmt))

    async def change_role(
        self,
        user_id: UserId,
        group_id: GroupId,
        new_role_id: RoleId,
    ) -> bool:
        stmt = (
            update(UsersToGroupsModel)
            .where(
                UsersToGroupsModel.user_id == user_id,
                UsersToGroupsModel.group_id == group_id,
                UsersToGroupsModel.deleted_at.is_(None),
            )
            .values(role_id=new_role_id)
            .returning(UsersToGroupsModel)
        )
        result = await self._session.scalar(stmt)
        await self._session.flush()
        return bool(result)

    async def join(
        self,
        user_id: UserId,
        group_id: GroupId,
        invite_id: InviteId,
    ) -> None:
        relation = UsersToGroupsModel(
            user_id=user_id,
            group_id=group_id,
            invite_id=invite_id,
            role_id=MEMBER_ROLE_ID,
        )
        try:
            self._session.add(relation)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise MaxHackError from e

    async def left(
        self,
        user_id: UserId,
        group_id: GroupId,
    ) -> bool:
        stmt = (
            update(UsersToGroupsModel)
            .where(
                UsersToGroupsModel.user_id == user_id,
                UsersToGroupsModel.group_id == group_id,
                UsersToGroupsModel.deleted_at.is_(None),
            )
            .values(deleted_at=func.now())
            .returning(UsersToGroupsModel)
        )
        result = await self._session.scalar(stmt)
        await self._session.flush()
        return bool(result)

    kick = left

    async def get_membership(
        self,
        *,
        user_id: UserId,
        group_id: GroupId,
    ) -> UsersToGroupsModel | None:
        stmt = (
            select(UsersToGroupsModel)
            .options(
                joinedload(UsersToGroupsModel.role),
                joinedload(UsersToGroupsModel.user),
            )
            .where(
                UsersToGroupsModel.user_id == user_id,
                UsersToGroupsModel.group_id == group_id,
            )
        )
        return await self._session.scalar(stmt)

    async def update_role(
        self,
        user_id: UserId,
        group_id: GroupId,
        role_id: RoleId,
    ) -> UsersToGroupsModel | None:
        stmt = (
            update(UsersToGroupsModel)
            .where(
                UsersToGroupsModel.user_id == user_id,
                UsersToGroupsModel.group_id == group_id,
                UsersToGroupsModel.deleted_at.is_(None),
            )
            .values(role_id=role_id)
            .returning(UsersToGroupsModel)
        )

        try:
            membership = await self._session.scalar(stmt)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise MaxHackError from e

        return membership
