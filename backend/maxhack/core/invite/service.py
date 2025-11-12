from typing import cast

from maxhack.core.exceptions import InviteNotFound
from maxhack.core.ids import GroupId, InviteKey, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.service import BaseService
from maxhack.core.utils.datehelp import datetime_now
from maxhack.infra.database.models import GroupModel, InviteModel
from maxhack.utils.utils import generate_invite_key


class InviteService(BaseService):
    async def recreate_invite(
        self,
        group_id: GroupId,
        creator_id: UserId,
    ) -> InviteModel:
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
            await self._invite_repo.update(
                current_invite.id,
                deleted_at=datetime_now(),
            )
        invite_obj = await self._invite_repo.create(
            key=key,
            group_id=group_id,
            creator_id=creator_id,
        )
        return invite_obj

    async def get_invite(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> InviteModel | None:
        await self._ensure_user_exists(user_id)
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        return await self._invite_repo.get_group_invite(group_id)

    async def delete_invite(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> None:
        await self._ensure_user_exists(user_id)
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        current_invite = await self._invite_repo.get_group_invite(group_id)
        if current_invite:
            await self._invite_repo.update(
                current_invite.id,
                deleted_at=datetime_now(),
            )

    async def is_valid_key(
        self,
        invite_key: InviteKey,
    ) -> tuple[InviteModel, GroupModel]:
        invite = await self._invite_repo.get_by_key(invite_key)
        if invite is None:
            raise InviteNotFound

        group = cast(GroupModel, await self._group_repo.get_by_id(invite.group_id))
        return invite, group
