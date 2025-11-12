import logging
from typing import cast

from maxhack.core.exceptions import (
    EntityNotFound,
    GroupNotFound,
    InvalidValue,
    InviteNotFound,
    NotEnoughRights,
    UserNotFound,
)
from maxhack.core.ids import GroupId, InviteKey, RoleId, TagId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.utils.datehelp import datetime_now
from maxhack.infra.database.models import (
    GroupModel,
    RoleModel,
    UsersToGroupsModel,
)
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.invite import InviteRepo
from maxhack.infra.database.repos.role import RoleRepo
from maxhack.infra.database.repos.tag import TagRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo

logger = logging.getLogger(__name__)


class GroupService:
    def __init__(
        self,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        invite_repo: InviteRepo,
        tag_repo: TagRepo,
        users_to_groups_repo: UsersToGroupsRepo,
        role_repo: RoleRepo,
    ) -> None:
        self._group_repo = group_repo
        self._users_to_groups_repo = users_to_groups_repo
        self._user_repo = user_repo
        self._invite_repo = invite_repo
        self._tag_repo = tag_repo
        self._role_repo = role_repo

    async def create_group(
        self,
        creator_id: UserId,
        name: str,
        description: str | None,
        timezone: int | None = None,
    ) -> GroupModel:
        creator = await self._user_repo.get_by_id(creator_id)
        if creator is None:
            raise UserNotFound

        if timezone is None:
            timezone = creator.timezone

        return await self._group_repo.create(
            name=name,
            description=description,
            creator_id=creator.id,
            timezone=timezone,
        )

    async def get_group(
        self,
        member_id: UserId,
        group_id: GroupId,
    ) -> tuple[GroupModel, RoleModel]:
        membership = await self.is_member(member_id, group_id)
        if membership is None:
            raise NotEnoughRights("Недостаточно прав для доступа к группе")

        group = await self._group_repo.get_by_id(group_id=group_id)
        if not group:
            raise GroupNotFound

        role = cast(RoleModel, await self._role_repo.get_role(membership.role_id))

        return group, role

    async def update_group(
        self,
        group_id: GroupId,
        editor_id: UserId,
        name: str | None,
        description: str | None,
        timezone: int = 0,
    ) -> GroupModel:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound

        if not await self.has_roles(
            CREATOR_ROLE_ID,
            EDITOR_ROLE_ID,
            user_id=editor_id,
            group_id=group_id,
        ):
            raise NotEnoughRights("Недостаточно прав для редактирования группы")

        return cast(
            GroupModel,
            await self._group_repo.update(
                group_id,
                name=name,
                description=description,
                timezone=timezone,
            ),
        )

    async def delete_group(
        self,
        group_id: GroupId,
        editor_id: UserId,
    ) -> None:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound

        if not await self.has_roles(
            CREATOR_ROLE_ID,
            user_id=editor_id,
            group_id=group_id,
        ):
            raise NotEnoughRights("Недостаточно прав для удаления группы")

        await self._group_repo.update(group_id, deleted_at=datetime_now())

    async def join_group(
        self,
        user_id: UserId,
        invite_key: InviteKey,
    ) -> GroupModel:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound

        invite = await self._invite_repo.get_by_key(invite_key)
        if invite is None:
            raise InviteNotFound

        group = cast(GroupModel, await self._group_repo.get_by_id(invite.group_id))

        existing = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group.id,
        )
        if existing is not None:
            raise InvalidValue("Пользователь уже состоит в группе")

        await self._users_to_groups_repo.join(
            user_id=user_id,
            group_id=group.id,
            invite_id=invite.id,
        )

        return group

    async def update_membership(
        self,
        group_id: GroupId,
        slave_id: UserId,
        master_id: UserId,
        role_id: RoleId | None = None,
        tags: list[TagId] | None = None,
    ) -> UsersToGroupsModel:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound

        if not await self.has_roles(
            CREATOR_ROLE_ID,
            EDITOR_ROLE_ID,
            user_id=master_id,
            group_id=group_id,
        ):
            raise NotEnoughRights("Недостаточно прав для редактирования участника")

        if role_id:
            membership = await self._users_to_groups_repo.update_role(
                user_id=slave_id,
                group_id=group_id,
                role_id=role_id,
            )
            if membership is None:
                raise EntityNotFound("Связь пользователя с группой не найдена")

        if tags is not None:
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

        return await self.get_member(slave_id, group_id, master_id)

    async def get_group_users(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> list[UsersToGroupsModel]:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound

        if not await self.is_member(user_id=user_id, group_id=group_id):
            raise NotEnoughRights("Пользователь не состоит в группе")

        return await self._users_to_groups_repo.group_users(group_id)

    async def remove_user_from_group(
        self,
        group_id: GroupId,
        slave_id: UserId,
        master_id: UserId,
    ) -> None:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound

        if not await self.has_roles(
            CREATOR_ROLE_ID,
            EDITOR_ROLE_ID,
            user_id=master_id,
            group_id=group_id,
        ):
            raise NotEnoughRights("Недостаточно прав для удаления участника")

        membership = await self._users_to_groups_repo.get_membership(
            user_id=slave_id,
            group_id=group_id,
        )
        if membership is None:
            raise EntityNotFound("Связь пользователя с группой не найдена")
        if membership.role_id == CREATOR_ROLE_ID:
            raise NotEnoughRights("Нельзя удалить создателя группы")

        await self._users_to_groups_repo.left(slave_id, group_id)

    async def get_member(
        self,
        user_id: UserId,
        group_id: GroupId,
        master_id: UserId,
    ) -> UsersToGroupsModel:
        if not await self.is_member(user_id=master_id, group_id=group_id):
            raise NotEnoughRights("Недостаточно прав для получения участника")

        membership = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None:
            raise UserNotFound

        return membership

    async def is_member(
        self,
        user_id: UserId,
        group_id: GroupId,
    ) -> UsersToGroupsModel:
        return await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )

    async def has_roles(
        self,
        *roles: RoleId,
        user_id: UserId,
        group_id: GroupId,
    ) -> bool:
        membership = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        return membership is not None and membership.role_id in roles
