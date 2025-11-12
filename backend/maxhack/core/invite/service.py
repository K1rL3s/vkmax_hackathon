from typing import cast

from maxhack.core.exceptions import (
    GroupNotFound,
    InviteNotFound,
    NotEnoughRights,
    UserNotFound,
)
from maxhack.core.ids import GroupId, InviteKey, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.utils.datehelp import datetime_now
from maxhack.infra.database.models import GroupModel, InviteModel, UsersToGroupsModel
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.invite import InviteRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo
from maxhack.utils.utils import generate_invite_key


class InviteService:
    def __init__(
        self,
        invite_repo: InviteRepo,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        users_to_groups_repo: UsersToGroupsRepo,
    ) -> None:
        self._invite_repo = invite_repo
        self._group_repo = group_repo
        self._user_repo = user_repo
        self._users_to_groups_repo = users_to_groups_repo

    async def _ensure_group_exists(self, group_id: GroupId | None) -> None:
        if group_id is None:
            return
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound

    async def _ensure_user_exists(self, user_id: UserId) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound

    async def _ensure_membership_role(
        self,
        *,
        user_id: UserId,
        group_id: GroupId,
        allowed_roles: set[int],
    ) -> UsersToGroupsModel:
        membership = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None or membership.role_id not in allowed_roles:
            raise NotEnoughRights
        return membership

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
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
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
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
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
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
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
