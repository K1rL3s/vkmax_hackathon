from typing import Any

from sqlalchemy import and_, func, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.exceptions import MaxHackError
from maxhack.core.ids import GroupId, RoleId, TagId, UserId
from maxhack.infra.database.models import (
    EventModel,
    TagModel,
    TagsToEvents,
    UserModel,
    UsersToGroupsModel,
    UsersToTagsModel,
)
from maxhack.infra.database.repos.base import BaseAlchemyRepo


class TagRepo(BaseAlchemyRepo):
    async def get_by_id(self, tag_id: TagId) -> TagModel | None:
        stmt = select(TagModel).where(TagModel.id == tag_id)
        return await self._session.scalar(stmt)

    async def create_tag(
        self,
        group_id: GroupId,
        name: str,
        description: str | None,
        color: str | None,
    ) -> TagModel:
        tag = TagModel(
            group_id=group_id,
            name=name,
            description=description,
            color=color,
        )
        self._session.add(tag)
        await self._session.flush()
        await self._session.refresh(tag)

        return tag

    async def delete_tag(self, tag_id: TagId, group_id: GroupId) -> None:
        events_subquery = (
            select(EventModel.id)
            .where(
                EventModel.group_id == group_id,
                EventModel.is_not_deleted,
            )
            .scalar_subquery()
        )

        update_tags_to_events_stmt = (
            update(TagsToEvents)
            .where(
                TagsToEvents.tag_id == tag_id,
                TagsToEvents.event_id.in_(events_subquery),
            )
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_tags_to_events_stmt)

        update_users_to_tags_stmt = (
            update(UsersToTagsModel)
            .where(
                UsersToTagsModel.tag_id == tag_id,
            )
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_users_to_tags_stmt)

        stmt = (
            update(TagModel)
            .where(
                TagModel.id == tag_id,
                TagModel.group_id == group_id,
                TagModel.is_not_deleted,
            )
            .values(deleted_at=func.now())
        )
        await self._session.execute(stmt)

    async def assign_tags_to_user(
        self,
        user_id: UserId,
        *tags_ids: TagId,
    ) -> None:
        assignment = [
            UsersToTagsModel(user_id=user_id, tag_id=tag_id) for tag_id in tags_ids
        ]
        self._session.add_all(assignment)
        await self._session.flush()

    async def remove_tags_from_user(
        self,
        user_id: UserId,
        *tags_ids: TagId,
    ) -> None:
        stmt = (
            update(UsersToTagsModel)
            .where(
                UsersToTagsModel.user_id == user_id,
                UsersToTagsModel.tag_id.in_([*tags_ids]),
            )
            .values(deleted_at=func.now())
        )
        await self._session.execute(stmt)

    async def list_group_tags(self, group_id: GroupId) -> list[TagModel]:
        stmt = select(TagModel).where(TagModel.group_id == group_id)
        return list(await self._session.scalars(stmt))

    async def list_user_tags(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> list[TagModel]:
        stmt = (
            select(TagModel)
            .join(UsersToTagsModel, TagModel.id == UsersToTagsModel.tag_id)
            .where(
                TagModel.group_id == group_id,
                UsersToTagsModel.user_id == user_id,
            )
        )

        return list(await self._session.scalars(stmt))

    async def list_tag_users(
        self,
        group_id: GroupId,
        tag_id: TagId,
    ) -> list[tuple[UserModel, RoleId]]:
        stmt = (
            select(UserModel, UsersToGroupsModel.role_id)
            .join(UsersToTagsModel, UsersToTagsModel.user_id == UserModel.id)
            .join(
                UsersToGroupsModel,
                and_(
                    UsersToGroupsModel.user_id == UserModel.id,
                    UsersToGroupsModel.group_id == group_id,
                ),
            )
            .where(UsersToTagsModel.tag_id == tag_id)
        )

        return list(await self._session.execute(stmt))

    async def update_tag(self, tag_id: TagId, **values: Any) -> TagModel | None:
        stmt = (
            update(TagModel)
            .where(TagModel.id == tag_id)
            .values(**values)
            .returning(TagModel)
        )
        try:
            tag = await self._session.scalar(stmt)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise MaxHackError from e

        return tag

    async def get_user_tag(
        self,
        user_id: UserId,
        tag_id: TagId,
    ) -> UsersToTagsModel | None:
        stmt = select(UsersToTagsModel).where(
            UsersToTagsModel.user_id == user_id,
            UsersToTagsModel.tag_id == tag_id,
        )
        return await self._session.scalar(stmt)
