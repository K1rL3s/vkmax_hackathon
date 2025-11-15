from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.exceptions import InvalidValue
from maxhack.core.ids import GroupId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID
from maxhack.database.models import (
    EventModel,
    EventNotifyModel,
    GroupModel,
    InviteModel,
    RespondModel,
    TagsToEvents,
    UsersToEvents,
    UsersToGroupsModel,
)
from maxhack.database.repos.base import BaseAlchemyRepo


class GroupRepo(BaseAlchemyRepo):
    async def get_by_id(self, group_id: GroupId) -> GroupModel | None:
        stmt = select(GroupModel).where(
            GroupModel.id == group_id,
            GroupModel.is_not_deleted,
        )
        return await self._session.scalar(stmt)

    async def create(
        self,
        name: str,
        description: str | None,
        creator_id: UserId,
        timezone: int = 0,
    ) -> GroupModel:
        group = GroupModel(name=name, description=description, timezone=timezone)
        try:
            self._session.add(group)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise InvalidValue from e

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
            raise InvalidValue from e

        return group

    async def update(self, group_id: GroupId, **values: Any) -> GroupModel | None:
        stmt = (
            update(GroupModel)
            .where(GroupModel.id == group_id, GroupModel.is_not_deleted)
            .values(**values)
            .returning(GroupModel)
        )
        try:
            group = await self._session.scalar(stmt)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise InvalidValue from e

        return group

    async def delete(self, group_id: GroupId) -> bool:

        events_subquery = (
            select(EventModel.id)
            .where(
                EventModel.group_id == group_id,
                EventModel.is_not_deleted,
            )
            .scalar_subquery()
        )

        if events_subquery is not None:
            update_tags_stmt = (
                update(TagsToEvents)
                .where(TagsToEvents.event_id.in_(events_subquery))
                .values(deleted_at=func.now())
            )
            await self._session.execute(update_tags_stmt)

            update_users_to_events_stmt = (
                update(UsersToEvents)
                .where(UsersToEvents.event_id.in_(events_subquery))
                .values(deleted_at=func.now())
            )
            await self._session.execute(update_users_to_events_stmt)

            update_notifies_stmt = (
                update(EventNotifyModel)
                .where(EventNotifyModel.event_id.in_(events_subquery))
                .values(deleted_at=func.now())
            )
            await self._session.execute(update_notifies_stmt)

            update_responds_stmt = (
                update(RespondModel)
                .where(RespondModel.event_id.in_(events_subquery))
                .values(deleted_at=func.now())
            )
            await self._session.execute(update_responds_stmt)

            update_events_stmt = (
                update(EventModel)
                .where(
                    EventModel.group_id == group_id,
                    EventModel.is_not_deleted,
                )
                .values(deleted_at=func.now())
            )
            await self._session.execute(update_events_stmt)

        update_users_to_groups_stmt = (
            update(UsersToGroupsModel)
            .where(UsersToGroupsModel.group_id == group_id)
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_users_to_groups_stmt)

        update_invites_stmt = (
            update(InviteModel)
            .where(InviteModel.group_id == group_id)
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_invites_stmt)

        stmt = (
            update(GroupModel)
            .where(
                GroupModel.id == group_id,
                GroupModel.is_not_deleted,
            )
            .values(deleted_at=func.now())
            .returning(GroupModel)
        )
        result = await self._session.scalar(stmt)

        return bool(result)
