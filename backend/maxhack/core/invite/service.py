from typing import cast

from maxhack.core.exceptions import InviteNotFound
from maxhack.core.ids import GroupId, InviteKey, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.service import BaseService
from maxhack.core.utils.datehelp import datetime_now
from maxhack.database.models import GroupModel, InviteModel
from maxhack.logger.setup import get_logger
from maxhack.utils.utils import generate_invite_key

logger = get_logger(__name__)


class InviteService(BaseService):
    async def recreate_invite(
        self,
        group_id: GroupId,
        creator_id: UserId,
    ) -> InviteModel:
        logger.debug(f"Recreating invite for group {group_id} by user {creator_id}")
        await self._ensure_user_exists(creator_id)
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=creator_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        key = generate_invite_key()
        current_invite = await self._invite_repo.get_group_invite(group_id)
        if current_invite:
            logger.debug(f"Deactivating old invite {current_invite.id}")
            await self._invite_repo.update(
                current_invite.id,
                deleted_at=datetime_now(),
            )
        invite_obj = await self._invite_repo.create(
            key=key,
            group_id=group_id,
            creator_id=creator_id,
        )
        logger.info(f"Invite {invite_obj.id} created successfully for group {group_id}")
        return invite_obj

    async def get_invite(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> InviteModel | None:
        logger.debug(f"Getting invite for group {group_id} by user {user_id}")
        await self._ensure_user_exists(user_id)
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        invite = await self._invite_repo.get_group_invite(group_id)
        if invite:
            logger.info(f"Invite {invite.id} found for group {group_id}")
        else:
            logger.info(f"No active invite found for group {group_id}")
        return invite

    async def delete_invite(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> None:
        logger.debug(f"Deleting invite for group {group_id} by user {user_id}")
        await self._ensure_user_exists(user_id)
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        current_invite = await self._invite_repo.get_group_invite(group_id)
        if current_invite:
            logger.debug(f"Deactivating invite {current_invite.id}")
            await self._invite_repo.update(
                current_invite.id,
                deleted_at=datetime_now(),
            )
            logger.info(
                f"Invite {current_invite.id} for group {group_id} deleted successfully",
            )
        else:
            logger.info(f"No active invite found for group {group_id} to delete")

    async def is_valid_key(
        self,
        invite_key: InviteKey,
    ) -> tuple[InviteModel, GroupModel]:
        logger.debug(f"Validating invite key {invite_key}")
        invite = await self._invite_repo.get_by_key(invite_key)
        if invite is None:
            logger.warning(f"Invite key {invite_key} not found")
            raise InviteNotFound

        group = cast(GroupModel, await self._group_repo.get_by_id(invite.group_id))
        logger.info(f"Invite key {invite_key} is valid for group {group.id}")
        return invite, group
