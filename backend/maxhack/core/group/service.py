from typing import cast

from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.exceptions import (
    EntityNotFound,
    GroupNotFound,
    InvalidValue,
    InviteNotFound,
    NotEnoughRights,
    UserNotFound,
)
from maxhack.core.group.consts import PRIVATE_GROUP_NAME
from maxhack.core.ids import GroupId, InviteKey, RoleId, TagId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.service import BaseService
from maxhack.core.utils.datehelp import datetime_now
from maxhack.database.models import (
    GroupModel,
    RoleModel,
    UsersToGroupsModel,
)
from maxhack.logger.setup import get_logger

logger = get_logger(__name__)


class GroupService(BaseService):
    async def create_group(
        self,
        master_id: UserId,
        name: str,
        description: str | None,
        timezone: int | None = None,
    ) -> GroupModel:
        logger.debug(f"Creating group with name '{name}' by user {master_id}")
        if name == PRIVATE_GROUP_NAME:
            logger.warning("Attempt to create group with reserved name")
            raise InvalidValue
        creator = await self._user_repo.get_by_id(master_id)
        if creator is None:
            logger.error(f"User {master_id} not found")
            raise UserNotFound

        if timezone is None:
            timezone = creator.timezone
            logger.debug(f"Timezone not provided, using creator's timezone: {timezone}")

        group = await self._group_repo.create(
            name=name,
            description=description,
            creator_id=creator.id,
            timezone=timezone,
        )
        logger.info(f"Group {group.id} created successfully")
        return group

    async def get_group(
        self,
        member_id: UserId,
        group_id: GroupId,
    ) -> tuple[GroupModel, RoleModel]:
        logger.debug(f"Getting group {group_id} for member {member_id}")
        membership = await self._ensure_membership_role(member_id, group_id)
        group = await self._ensure_group_exists(group_id)
        role = cast(RoleModel, await self._role_repo.get_role(membership.role_id))
        logger.info(
            f"Group {group_id} and role {role.id} retrieved for member {member_id}",
        )
        return group, role

    async def update_group(
        self,
        group_id: GroupId,
        master_id: UserId,
        name: str | None,
        description: str | None,
        timezone: int = 0,
    ) -> GroupModel:
        logger.debug(
            f"Updating group {group_id} by user {master_id} with name '{name}' and description '{description}'",
        )
        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )
        group = await self._ensure_group_exists(group_id)
        if group.name == PRIVATE_GROUP_NAME:
            logger.warning("Attempt to update group with reserved name")
            raise InvalidValue

        updated_group = await self._group_repo.update(
            group_id,
            name=name,
            description=description,
            timezone=timezone,
        )
        if updated_group is None:
            logger.error(f"Group {group_id} not found for update")
            raise GroupNotFound
        logger.info(f"Group {group_id} updated successfully")
        return cast(GroupModel, updated_group)

    async def delete_group(
        self,
        group_id: GroupId,
        editor_id: UserId,
    ) -> None:
        logger.debug(f"Deleting group {group_id} by user {editor_id}")
        group = await self._ensure_group_exists(group_id)
        if group.name == PRIVATE_GROUP_NAME:
            logger.warning("Attempt to delete group with reserved name")
            raise InvalidValue
        await self._ensure_membership_role(editor_id, group_id, (CREATOR_ROLE_ID,))
        await self._group_repo.update(group_id, deleted_at=datetime_now())
        logger.info(f"Group {group_id} deleted successfully")

    async def join_group(
        self,
        user_id: UserId,
        invite_key: InviteKey,
    ) -> GroupModel:
        logger.debug(f"User {user_id} joining group with invite key {invite_key}")
        await self._ensure_user_exists(user_id)

        invite = await self._invite_repo.get_by_key(invite_key)
        if invite is None:
            logger.warning(f"Invite key {invite_key} not found")
            raise InviteNotFound

        group = await self._ensure_group_exists(invite.group_id)
        if group.name == PRIVATE_GROUP_NAME:
            logger.warning("Attempt to join group with reserved name")
            raise InvalidValue

        existing = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group.id,
        )
        if existing is not None:
            logger.warning(f"User {user_id} already in group {group.id}")
            raise InvalidValue("Пользователь уже состоит в группе")

        await self._users_to_groups_repo.join(
            user_id=user_id,
            group_id=group.id,
            invite_id=invite.id,
        )
        logger.info(f"User {user_id} joined group {group.id} successfully")

        return group

    async def update_membership(
        self,
        group_id: GroupId,
        slave_id: UserId,
        master_id: UserId,
        role_id: RoleId | None = None,
        tags: list[TagId] | None = None,
        notify_mode: NotifyMode | None = None,
    ) -> UsersToGroupsModel:
        logger.debug(
            f"Updating membership for user {slave_id} in group {group_id} by user {master_id} with role_id={role_id}, tags={tags}, notify_mode={notify_mode}",
        )
        group = await self._ensure_group_exists(group_id)

        master_membership = await self._ensure_membership_role(master_id, group_id)
        slave_membership = await self._ensure_membership_role(slave_id, group_id)

        if role_id:
            logger.debug(f"Updating role for user {slave_id} to {role_id}")
            if group.name == PRIVATE_GROUP_NAME:
                logger.warning("Attempt to update role in group with reserved name")
                raise InvalidValue
            if master_membership.role_id not in (CREATOR_ROLE_ID, EDITOR_ROLE_ID):
                logger.warning(
                    f"User {master_id} has no rights to update role in group {group_id}",
                )
                raise NotEnoughRights
            if slave_membership.role_id == CREATOR_ROLE_ID:
                logger.warning(
                    f"Attempt to change role of creator {slave_id} in group {group_id}",
                )
                raise NotEnoughRights
            await self._users_to_groups_repo.update_role(
                user_id=slave_id,
                group_id=group_id,
                role_id=role_id,
            )
            logger.info(
                f"Role for user {slave_id} in group {group_id} updated to {role_id}",
            )

        if notify_mode:
            logger.debug(f"Updating notify mode for user {slave_id} to {notify_mode}")
            if master_id != slave_id:
                logger.warning(
                    f"User {master_id} has no rights to update notify mode for user {slave_id}",
                )
                raise NotEnoughRights
            await self._users_to_groups_repo.update_notify_mode(
                user_id=slave_id,
                group_id=group_id,
                notify_mode=notify_mode,
            )
            logger.info(
                f"Notify mode for user {slave_id} in group {group_id} updated to {notify_mode}",
            )

        if tags is not None:
            logger.debug(f"Updating tags for user {slave_id} to {tags}")
            if master_membership.role_id not in (CREATOR_ROLE_ID, EDITOR_ROLE_ID):
                logger.warning(
                    f"User {master_id} has no rights to update tags in group {group_id}",
                )
                raise NotEnoughRights
            member_tags = await self._tag_repo.list_user_tags(
                group_id=group_id,
                user_id=slave_id,
            )
            member_tag_ids = {tag.id for tag in member_tags}
            to_add = set(tags).difference(member_tag_ids)
            to_remove = set(member_tag_ids).difference(tags)
            logger.info(
                "Updating tags for user %d in group %d: adding %s, removing %s",
                slave_id,
                group_id,
                to_add,
                to_remove,
            )
            await self._tag_repo.assign_tags_to_user(slave_id, *to_add)
            await self._tag_repo.remove_tags_from_user(slave_id, *to_remove)
            logger.info(f"Tags for user {slave_id} in group {group_id} updated")

        return await self.get_member(slave_id, group_id, master_id)

    async def get_group_users(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> list[UsersToGroupsModel]:
        logger.debug(f"Getting users for group {group_id} by user {user_id}")
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            logger.error(f"Group {group_id} not found")
            raise GroupNotFound

        if not await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        ):
            logger.warning(f"User {user_id} is not in group {group_id}")
            raise NotEnoughRights

        users = await self._users_to_groups_repo.group_users(group_id)
        logger.info(f"Found {len(users)} users in group {group_id}")
        return users

    async def remove_user_from_group(
        self,
        group_id: GroupId,
        slave_id: UserId,
        master_id: UserId,
    ) -> None:
        logger.debug(
            f"Removing user {slave_id} from group {group_id} by user {master_id}",
        )
        group = await self._ensure_group_exists(group_id)
        if group.name == PRIVATE_GROUP_NAME:
            logger.warning("Attempt to remove user from group with reserved name")
            raise InvalidValue

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        membership = await self._users_to_groups_repo.get_membership(
            user_id=slave_id,
            group_id=group_id,
        )
        if membership is None:
            logger.error(f"User {slave_id} is not in group {group_id}")
            raise EntityNotFound("Связь пользователя с группой не найдена")
        if membership.role_id == CREATOR_ROLE_ID:
            logger.warning(
                f"Attempt to remove creator {slave_id} from group {group_id}",
            )
            raise NotEnoughRights

        await self._users_to_groups_repo.left(slave_id, group_id)
        logger.info(f"User {slave_id} removed from group {group_id} successfully")

    async def get_member(
        self,
        user_id: UserId,
        group_id: GroupId,
        master_id: UserId,
    ) -> UsersToGroupsModel:
        logger.debug(
            f"Getting member {user_id} from group {group_id} by user {master_id}",
        )
        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        membership = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None:
            logger.error(f"User {user_id} is not in group {group_id}")
            raise UserNotFound

        logger.info(f"Member {user_id} from group {group_id} retrieved successfully")
        return membership
