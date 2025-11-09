from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import MaxChatId, MaxId, UserId
from maxhack.infra.database.models import (
    GroupModel,
    RoleModel,
    UserModel,
)
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo


class UserService:
    def __init__(
        self,
        user_repo: UserRepo,
        group_repo: GroupRepo,
        users_to_groups_repo: UsersToGroupsRepo,
    ) -> None:
        self._user_repo = user_repo
        self._group_repo = group_repo
        self._users_to_groups_repo = users_to_groups_repo

    async def create_user(
        self,
        max_id: MaxId,
        max_chat_id: MaxChatId,
        first_name: str,
        last_name: str | None = None,
        phone: str | None = None,
    ) -> UserModel:
        exists = await self._user_repo.get_by_max_id(max_id)
        if exists is not None:
            raise InvalidValue("Пользователь с таким max_id уже существует")

        return await self._user_repo.create_user(
            max_id=max_id,
            max_chat_id=max_chat_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

    async def get_user_by_id(
        self,
        user_id: UserId,
    ) -> UserModel:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFound("Пользователь не найден")
        return user

    async def update_user(
        self,
        user_id: UserId,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
    ) -> UserModel:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFound("Пользователь не найден")

        values: dict[str, str] = {}
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if phone is not None:
            values["phone"] = phone

        user = await self._user_repo.update_user(user_id, **values)
        if user is None:
            raise EntityNotFound("Пользователь не найден")

        return user

    async def get_user_groups(
        self,
        user_id: UserId,
        master_id: UserId,
    ) -> list[tuple[GroupModel, RoleModel]]:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFound("Пользователь не найден")

        requester = await self._user_repo.get_by_id(master_id)
        if requester is None:
            raise EntityNotFound("Пользователь не найден")

        if master_id != user_id:
            raise NotEnoughRights("Недостаточно прав для просмотра групп пользователя")

        return await self._users_to_groups_repo.user_groups(user_id)
