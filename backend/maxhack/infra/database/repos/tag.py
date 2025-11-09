from typing import Any

from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.exceptions import MaxHackError
from maxhack.core.ids import GroupId, TagId, UserId
from maxhack.infra.database.models import (
    TagModel,
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
        descriptions: str | None,
        color: str | None,
    ) -> TagModel:
        tag = TagModel(
            group_id=group_id,
            name=name,
            descriptions=descriptions,
            color=color,
        )
        self._session.add(tag)
        await self._session.flush()
        await self._session.refresh(tag)

        return tag

    async def delete_tag(self, tag_id: TagId) -> None:
        tag = await self.get_by_id(tag_id)
        if tag:
            await self._session.execute(
                delete(UsersToTagsModel).where(UsersToTagsModel.tag_id == tag_id),
            )
            await self._session.delete(tag)
            await self._session.flush()

    async def assign_tag_to_user(
        self,
        user_id: UserId,
        tag_id: TagId,
    ) -> UsersToTagsModel:
        assignment = UsersToTagsModel(user_id=user_id, tag_id=tag_id)
        self._session.add(assignment)
        await self._session.flush()
        await self._session.refresh(assignment)

        return assignment

        await self._session.flush()

    async def remove_tag_from_user(
        self,
        user_id: UserId,
        tag_id: TagId,
    ) -> None:
        assignment = await self.get_user_tag_assignment(user_id=user_id, tag_id=tag_id)
        if assignment:
            await self._session.delete(assignment)
            await self._session.flush()

    async def list_group_tags(self, group_id: GroupId) -> list[TagModel]:
        stmt = select(TagModel).where(TagModel.group_id == group_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

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

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_tag_users(
        self,
        group_id: GroupId,
        tag_id: TagId,
    ) -> list[tuple[UserModel, int]]:
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

        result = await self._session.execute(stmt)
        return result.all()

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
