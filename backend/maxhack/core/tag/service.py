from maxhack.core.exceptions import (
    EntityNotFound,
    InvalidValue,
    TagNotFound,
)
from maxhack.core.ids import GroupId, RoleId, TagId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.service import BaseService
from maxhack.infra.database.models import TagModel, UserModel


class TagService(BaseService):
    async def create_tag(
        self,
        group_id: GroupId,
        master_id: UserId,
        name: str,
        description: str | None,
        color: str | None,
    ) -> TagModel:
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        return await self._tag_repo.create_tag(
            group_id=group_id,
            name=name,
            description=description,
            color=color,
        )

    async def update_tag(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
    ) -> TagModel:
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        values: dict[str, str] = {}
        if name is not None:
            values["name"] = name
        if description is not None:
            values["description"] = description
        if color is not None:
            values["color"] = color

        tag = await self._tag_repo.update_tag(tag_id, **values)
        if tag is None:
            raise TagNotFound

        return tag

    async def delete_tag(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
    ) -> None:
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        await self._tag_repo.delete_tag(tag_id, group_id)

    async def assign_tag_to_user(
        self,
        group_id: GroupId,
        tag_id: TagId,
        user_id: UserId,
        master_id: UserId,
    ) -> None:
        await self._ensure_group_exists(group_id)
        tag = await self._ensure_tag_exists(tag_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        await self._ensure_user_exists(user_id)

        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
        )

        existing = await self._tag_repo.get_user_tag(
            user_id=user_id,
            tag_id=tag.id,
        )
        if existing is not None:
            raise InvalidValue("Тег уже назначен пользователю")

        await self._tag_repo.assign_tags_to_user(user_id, tag.id)

    async def remove_tag_from_user(
        self,
        group_id: GroupId,
        tag_id: TagId,
        user_id: UserId,
        master_id: UserId,
    ) -> None:
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        assignment = await self._tag_repo.get_user_tag(
            user_id=user_id,
            tag_id=tag_id,
        )
        if assignment is None:
            raise EntityNotFound("Назначение тега не найдено")

        await self._tag_repo.remove_tags_from_user(user_id, tag_id)

    async def list_group_tags(
        self,
        group_id: GroupId,
        master_id: UserId,
    ) -> list[TagModel]:
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        return await self._tag_repo.list_group_tags(group_id)

    async def list_user_tags(
        self,
        group_id: GroupId,
        user_id: UserId,
        master_id: UserId,
    ) -> list[TagModel]:
        await self._ensure_group_exists(group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
        )

        return await self._tag_repo.list_user_tags(group_id, user_id)

    async def list_tag_users(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
    ) -> list[tuple[UserModel, RoleId]]:
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        return await self._tag_repo.list_tag_users(group_id, tag_id)
