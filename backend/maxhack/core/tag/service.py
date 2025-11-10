from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import GroupId, TagId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID
from maxhack.infra.database.models import (
    TagModel,
    UserModel,
    UsersToGroupsModel,
    UsersToTagsModel,
)
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.tag import TagRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo


class TagService:
    def __init__(
        self,
        tag_repo: TagRepo,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        users_to_group_repo: UsersToGroupsRepo,
    ) -> None:
        self._tag_repo = tag_repo
        self._group_repo = group_repo
        self._user_repo = user_repo
        self._users_to_group_repo = users_to_group_repo

    async def _ensure_group_exists(self, group_id: GroupId) -> None:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise EntityNotFound("Группа не найдена")

    async def _ensure_user_exists(self, user_id: UserId) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFound("Пользователь не найден")

    async def _ensure_tag_exists(
        self,
        tag_id: TagId,
        group_id: GroupId,
    ) -> TagModel:
        tag = await self._tag_repo.get_by_id(tag_id)
        if tag is None or tag.group_id != group_id:
            raise EntityNotFound("Тег не найден")
        return tag

    async def _ensure_membership_role(
        self,
        *,
        user_id: UserId,
        group_id: GroupId,
        allowed_roles: set[int],
    ) -> UsersToGroupsModel:
        membership = await self._users_to_group_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None or membership.role_id not in allowed_roles:
            raise NotEnoughRights("Недостаточно прав")
        return membership

    async def create_tag(
        self,
        group_id: GroupId,
        master_id: UserId,
        name: str,
        descriptions: str | None,
        color: str | None,
    ) -> TagModel:
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
        )

        return await self._tag_repo.create_tag(
            group_id=group_id,
            name=name,
            descriptions=descriptions,
            color=color,
        )

    async def update_tag(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
        name: str | None = None,
        descriptions: str | None = None,
        color: str | None = None,
    ) -> TagModel:
        await self._ensure_group_exists(group_id)
        tag = await self._ensure_tag_exists(tag_id, group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
        )

        values: dict[str, str] = {}
        if name is not None:
            values["name"] = name
        if descriptions is not None:
            values["descriptions"] = descriptions
        if color is not None:
            values["color"] = color

        tag = await self._tag_repo.update_tag(tag_id, **values)
        if tag is None:
            raise EntityNotFound("Тег не найден")

        return tag

    async def delete_tag(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
    ) -> None:
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id, group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
        )

        await self._tag_repo.delete_tag(tag_id)

    async def assign_tag_to_user(
        self,
        group_id: GroupId,
        tag_id: TagId,
        user_id: UserId,
        master_id: UserId,
    ) -> None:
        await self._ensure_group_exists(group_id)
        tag = await self._ensure_tag_exists(tag_id, group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
        )

        await self._ensure_user_exists(user_id)

        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID},
        )

        existing = await self._tag_repo.get_user_tag(
            user_id=user_id,
            tag_id=tag.id,
        )
        if existing is not None:
            raise InvalidValue("Тег уже назначен пользователю")

        await self._tag_repo.assign_tags_to_user(
            user_id,
            tag.id,
        )

    async def remove_tag_from_user(
        self,
        group_id: GroupId,
        tag_id: TagId,
        user_id: UserId,
        master_id: UserId,
    ) -> None:
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id, group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
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
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID},
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
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID},
        )

        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID},
        )

        return await self._tag_repo.list_user_tags(group_id, user_id)

    async def list_tag_users(
        self,
        group_id: GroupId,
        tag_id: TagId,
        master_id: UserId,
    ) -> list[tuple[UserModel, int]]:
        await self._ensure_group_exists(group_id)
        await self._ensure_tag_exists(tag_id, group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
            allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID},
        )

        return await self._tag_repo.list_tag_users(group_id, tag_id)
