from typing import Any

from maxhack.core.exceptions import (
    GroupNotFound,
    InvalidValue,
    NotEnoughRights,
    UserNotFound,
)
from maxhack.core.group.consts import PRIVATE_GROUP_NAME
from maxhack.core.ids import MaxChatId, MaxId, TagId, UserId
from maxhack.core.utils.timezones import TIMEZONES
from maxhack.database.models import (
    EventModel,
    GroupModel,
    RoleModel,
    UserModel,
)
from maxhack.database.repos.event import EventRepo
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
        event_repo: EventRepo,
    ) -> None:
        self._user_repo = user_repo
        self._group_repo = group_repo
        self._users_to_groups_repo = users_to_groups_repo
        self._event_repo = event_repo

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
        **kwargs: Any,
    ) -> UserModel:
        logger.debug(f"Updating user {user_id}")

        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            logger.error(f"User {user_id} not found for update")
            raise UserNotFound

        values = {key: value for key, value in kwargs.items() if value is not None}

        if "timezone" in values and values["timezone"] not in TIMEZONES:
            raise InvalidValue

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

    async def get_personal_group(self, user_id: UserId) -> GroupModel:
        logger.debug("Getting personal group for user %d", user_id)
        user = await self.get_user_by_id(user_id)
        group = await self._users_to_groups_repo.personal_group(user.id)
        if not group:
            logger.error("Personal group for user %d not found", user.id)
            raise GroupNotFound(message="Что то пошло не так, личная группа не найдена")

        logger.info("Personal group for user %d retrieved successfully", user.id)
        return group

    async def get_personal_events(
        self,
        user_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> list[EventModel]:
        logger.debug(
            "Getting personal events for user %d with tags %s",
            user_id,
            tag_ids,
        )
        personal_group = await self.get_personal_group(user_id)
        events = await self._event_repo.get_by_group_id(
            group_id=personal_group.id,
            tag_ids=tag_ids,
        )
        logger.info(
            "%d Personal events for user %d retrieved successfully",
            len(events),
            user_id,
        )
        return events
