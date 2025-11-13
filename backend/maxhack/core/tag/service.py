from maxhack.core.exceptions import (
    EntityNotFound,
    InvalidValue,
    TagNotFound,
)
from maxhack.core.ids import GroupId, RoleId, TagId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.service import BaseService
from maxhack.database.models import TagModel, UserModel
from maxhack.logger.setup import get_logger

logger = get_logger(__name__)


class TagService(BaseService):
    async def create_tag(
        self,
        group_id: GroupId,
        master_id: UserId,
        name: str,
        description: str | None,
        color: str | None,
    ) -> TagModel:
        logger.debug(
            f"Creating tag with name '{name}' in group {group_id} by user {master_id}",
        )
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        tag = await self._tag_repo.create_tag(
            group_id=group_id,
            name=name,
            description=description,
            color=color,
        )
        logger.info(f"Tag {tag.id} created successfully in group {group_id}")
        return tag

    async def update_tag(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
    ) -> TagModel:
        logger.debug(
            f"Updating tag {tag_id} in group {group_id} by user {master_id} with name='{name}', description='{description}', color='{color}'",
        )
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
            logger.error(f"Tag {tag_id} not found for update")
            raise TagNotFound

        logger.info(f"Tag {tag_id} updated successfully")
        return tag

    async def delete_tag(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
    ) -> None:
        logger.debug(f"Deleting tag {tag_id} in group {group_id} by user {master_id}")
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        await self._tag_repo.delete_tag(tag_id, group_id)
        logger.info(f"Tag {tag_id} in group {group_id} deleted successfully")

    async def assign_tag_to_user(
        self,
        group_id: GroupId,
        tag_id: TagId,
        user_id: UserId,
        master_id: UserId,
    ) -> None:
        logger.debug(
            f"Assigning tag {tag_id} to user {user_id} in group {group_id} by user {master_id}",
        )
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
            logger.warning(f"Tag {tag_id} already assigned to user {user_id}")
            raise InvalidValue("Тег уже назначен пользователю")

        await self._tag_repo.assign_tags_to_user(user_id, tag.id)
        logger.info(f"Tag {tag_id} assigned to user {user_id} successfully")

    async def remove_tag_from_user(
        self,
        group_id: GroupId,
        tag_id: TagId,
        user_id: UserId,
        master_id: UserId,
    ) -> None:
        logger.debug(
            f"Removing tag {tag_id} from user {user_id} in group {group_id} by user {master_id}",
        )
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
            logger.error(f"Tag {tag_id} is not assigned to user {user_id}")
            raise EntityNotFound("Назначение тега не найдено")

        await self._tag_repo.remove_tags_from_user(user_id, tag_id)
        logger.info(f"Tag {tag_id} removed from user {user_id} successfully")

    async def list_group_tags(
        self,
        group_id: GroupId,
        master_id: UserId,
    ) -> list[TagModel]:
        logger.debug(f"Listing tags for group {group_id} by user {master_id}")
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        tags = await self._tag_repo.list_group_tags(group_id)
        logger.info(f"Found {len(tags)} tags for group {group_id}")
        return tags

    async def list_user_tags(
        self,
        group_id: GroupId,
        user_id: UserId,
        master_id: UserId,
    ) -> list[TagModel]:
        logger.debug(
            f"Listing tags for user {user_id} in group {group_id} by user {master_id}",
        )
        await self._ensure_group_exists(group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
        )

        tags = await self._tag_repo.list_user_tags(group_id, user_id)
        logger.info(f"Found {len(tags)} tags for user {user_id} in group {group_id}")
        return tags

    async def list_tag_users(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
    ) -> list[tuple[UserModel, RoleId]]:
        logger.debug(
            f"Listing users for tag {tag_id} in group {group_id} by user {master_id}",
        )
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        users = await self._tag_repo.list_tag_users(group_id, tag_id)
        logger.info(f"Found {len(users)} users for tag {tag_id} in group {group_id}")
        return users
