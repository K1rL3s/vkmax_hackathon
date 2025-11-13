from typing import Any

from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.exceptions import (
    InvalidValue,
    NotEnoughRights,
    UserNotFound,
)
from maxhack.core.group.consts import PRIVATE_GROUP_NAME
from maxhack.core.ids import MaxChatId, MaxId, UserId
from maxhack.database.models import (
    GroupModel,
    RoleModel,
    UserModel,
)
from maxhack.database.repos.group import GroupRepo
from maxhack.database.repos.user import UserRepo
from maxhack.database.repos.users_to_groups import UsersToGroupsRepo
from maxhack.logger.setup import get_logger

logger = get_logger(__name__)


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
        timezone: int = 0,
    ) -> UserModel:
        logger.debug(f"Creating user with max_id {max_id}")
        exists = await self._user_repo.get_by_max_id(max_id)
        if exists is not None:
            logger.warning(f"User with max_id {max_id} already exists")
            raise InvalidValue("Пользователь с таким max_id уже существует")

        user = await self._user_repo.create_user(
            max_id=max_id,
            max_chat_id=max_chat_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            timezone=timezone,
        )
        logger.info(f"User {user.id} created successfully")

        await self._group_repo.create(
            name=PRIVATE_GROUP_NAME,
            creator_id=user.id,
            timezone=timezone,
            description=None,
        )
        logger.debug(f"Private group for user {user.id} created successfully")
        return user

    async def get_user_by_id(
        self,
        user_id: UserId,
    ) -> UserModel:
        logger.debug(f"Getting user by id {user_id}")
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            logger.error(f"User with id {user_id} not found")
            raise UserNotFound
        logger.info(f"User {user_id} retrieved successfully")
        return user

    async def get_user_by_max_id(
        self,
        max_id: MaxId,
    ) -> UserModel:
        logger.debug(f"Getting user by max_id {max_id}")
        user = await self._user_repo.get_by_max_id(max_id)
        if user is None:
            logger.error(f"User with max_id {max_id} not found")
            raise UserNotFound
        logger.info(f"User with max_id {max_id} retrieved successfully")
        return user

    async def update_user(
        self,
        user_id: UserId,
        first_name: str | None = None,
        last_name: str | None = None,
        photo: str | None = None,
        phone: str | None = None,
        notify_mode: NotifyMode | None = None,
        timezone: int | None = None,
    ) -> UserModel:
        logger.debug(f"Updating user {user_id}")
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            logger.error(f"User {user_id} not found for update")
            raise UserNotFound

        # TODO: ???????
        values: dict[str, Any] = {}
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if photo is not None:
            values["photo"] = photo
        if phone is not None:
            values["phone"] = phone
        if timezone is not None:
            values["timezone"] = timezone
        if notify_mode is not None:
            values["notify_mode"] = notify_mode
        logger.debug(f"Updating user {user_id} with values {values}")
        user = await self._user_repo.update_user(user_id, **values)
        if user is None:
            logger.error(f"User {user_id} not found after update")
            raise UserNotFound

        logger.info(f"User {user_id} updated successfully")
        return user

    async def get_user_groups(
        self,
        user_id: UserId,
        master_id: UserId,
    ) -> list[tuple[GroupModel, RoleModel]]:
        logger.debug(f"Getting groups for user {user_id} by user {master_id}")
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            logger.error(f"User {user_id} not found")
            raise UserNotFound

        if user_id != master_id:
            logger.warning(
                f"User {master_id} has no rights to view groups of user {user_id}",
            )
            raise NotEnoughRights

        groups = await self._users_to_groups_repo.user_groups(user_id)
        logger.info(f"Found {len(groups)} groups for user {user_id}")
        return groups
