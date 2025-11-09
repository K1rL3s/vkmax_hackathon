from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import EventId, GroupId, TagId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.infra.database.models import EventModel, TagModel, UsersToGroupsModel
from maxhack.infra.database.repos.event import EventRepo
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.tag import TagRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo


class EventService:
    def __init__(
        self,
        event_repo: EventRepo,
        tag_repo: TagRepo,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        users_to_group_repo: UsersToGroupsRepo,
    ) -> None:
        self._event_repo = event_repo
        self._tag_repo = tag_repo
        self._group_repo = group_repo
        self._user_repo = user_repo
        self._users_to_group_repo = users_to_group_repo

    async def _ensure_group_exists(self, group_id: GroupId | None) -> None:
        if group_id is None:
            return
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise EntityNotFound("Группа не найдена")

    async def _ensure_user_exists(self, user_id: UserId) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFound("Пользователь не найден")

    async def _ensure_event_exists(self, event_id: EventId) -> EventModel:
        event = await self._event_repo.get_by_id(event_id)
        if event is None:
            raise EntityNotFound("Событие не найдено")
        return event

    async def _ensure_tag_exists(self, tag_id: TagId) -> TagModel:
        tag = await self._tag_repo.get_by_id(tag_id)
        if tag is None:
            raise EntityNotFound("Тег не найден")
        return tag

    async def _ensure_membership_role(
        self,
        *,
        user_id: UserId,
        group_id: GroupId | None,
        allowed_roles: set[int],
    ) -> UsersToGroupsModel | None:
        if group_id is None:
            return None
        membership = await self._users_to_group_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None or membership.role_id not in allowed_roles:
            raise NotEnoughRights("Недостаточно прав")
        return membership

    async def get_event(self, event_id: EventId, user_id: UserId) -> EventModel:
        event = await self._ensure_event_exists(event_id)

        # Проверяем доступ: пользователь должен быть либо создателем, либо в группе события, либо в списке пользователей события
        if event.group_id is not None:
            membership = await self._users_to_group_repo.get_membership(
                user_id=user_id,
                group_id=event.group_id,
            )
            if membership is None:
                # Проверяем, есть ли пользователь в списке пользователей события
                is_in_event = await self._event_repo.check_user_in_event(
                    event_id,
                    user_id,
                )
                if not is_in_event and event.creator_id != user_id:
                    raise NotEnoughRights("Недостаточно прав для просмотра события")
        elif event.creator_id != user_id:
            # Если события без группы, только создатель может просматривать
            is_in_event = await self._event_repo.check_user_in_event(event_id, user_id)
            if not is_in_event:
                raise NotEnoughRights("Недостаточно прав для просмотра события")

        return event

    async def create_event(
        self,
        title: str,
        description: str | None,
        cron: str,
        is_cycle: bool,
        type: str,
        creator_id: UserId,
        group_id: GroupId | None,
    ) -> EventModel:
        await self._ensure_user_exists(creator_id)
        await self._ensure_group_exists(group_id)

        if group_id is not None:
            await self._ensure_membership_role(
                user_id=creator_id,
                group_id=group_id,
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
            )

        return await self._event_repo.create(
            title=title,
            description=description,
            cron=cron,
            is_cycle=is_cycle,
            type=type,
            creator_id=creator_id,
            group_id=group_id,
        )

    async def update_event(
        self,
        event_id: EventId,
        user_id: UserId,
        title: str | None = None,
        description: str | None = None,
        cron: str | None = None,
        is_cycle: bool | None = None,
        type: str | None = None,
    ) -> EventModel:
        event = await self._ensure_event_exists(event_id)

        # Проверяем права: только создатель или пользователь с ролью 1 или 2 в группе
        if event.group_id is not None:
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
            )
        elif event.creator_id != user_id:
            raise NotEnoughRights("Недостаточно прав для редактирования события")

        values = {}
        if title is not None:
            values["title"] = title
        if description is not None:
            values["description"] = description
        if cron is not None:
            values["cron"] = cron
        if is_cycle is not None:
            values["is_cycle"] = is_cycle
        if type is not None:
            values["type"] = type

        updated_event = await self._event_repo.update(event_id, **values)
        if updated_event is None:
            raise EntityNotFound("Событие не найдено")

        return updated_event

    async def delete_event(self, event_id: EventId, user_id: UserId) -> None:
        event = await self._ensure_event_exists(event_id)

        # Проверяем права: только создатель или пользователь с ролью 1 или 2 в группе
        if event.group_id is not None:
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
            )
        elif event.creator_id != user_id:
            raise NotEnoughRights("Недостаточно прав для удаления события")

        success = await self._event_repo.delete(event_id)
        if not success:
            raise EntityNotFound("Событие не найдено")

    async def add_tag_to_event(
        self,
        event_id: EventId,
        tag_id: TagId,
        user_id: UserId,
    ) -> None:
        event = await self._ensure_event_exists(event_id)
        tag = await self._ensure_tag_exists(tag_id)

        # Проверяем права: только создатель или пользователь с ролью 1 или 2 в группе
        if event.group_id is not None:
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
            )
            # Проверяем, что тег принадлежит той же группе
            if tag.group_id != event.group_id:
                raise InvalidValue("Тег не принадлежит группе события")
        elif event.creator_id != user_id:
            raise NotEnoughRights("Недостаточно прав для добавления тега")

        # Проверяем, не добавлен ли уже тег
        event_tags = await self._event_repo.get_event_tags(event_id)
        if tag_id in event_tags:
            raise InvalidValue("Тег уже добавлен к событию")

        await self._event_repo.add_tag(event_id, tag_id)

    async def add_user_to_event(
        self,
        event_id: EventId,
        target_user_id: UserId,
        user_id: UserId,
    ) -> None:
        event = await self._ensure_event_exists(event_id)
        await self._ensure_user_exists(target_user_id)

        # Проверяем права: только создатель или пользователь с ролью 1 или 2 в группе
        if event.group_id is not None:
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
            )
            # Проверяем, что целевой пользователь тоже в группе
            target_membership = await self._users_to_group_repo.get_membership(
                user_id=target_user_id,
                group_id=event.group_id,
            )
            if target_membership is None:
                raise InvalidValue("Пользователь не состоит в группе события")
        elif event.creator_id != user_id:
            raise NotEnoughRights("Недостаточно прав для добавления пользователя")

        # Проверяем, не добавлен ли уже пользователь
        is_in_event = await self._event_repo.check_user_in_event(
            event_id,
            target_user_id,
        )
        if is_in_event:
            raise InvalidValue("Пользователь уже добавлен к событию")

        await self._event_repo.add_user(event_id, target_user_id)

    async def get_group_events(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> list[EventModel]:
        await self._ensure_group_exists(group_id)

        # Проверяем, что пользователь состоит в группе
        membership = await self._users_to_group_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None:
            raise NotEnoughRights("Пользователь не состоит в группе")

        return await self._event_repo.get_by_group(group_id)

    async def get_user_events(self, user_id: UserId) -> list[EventModel]:
        await self._ensure_user_exists(user_id)
        return await self._event_repo.get_created_by_user(user_id)

    async def get_other_user_events(
        self,
        target_user_id: UserId,
        user_id: UserId,
    ) -> list[EventModel]:
        await self._ensure_user_exists(target_user_id)
        await self._ensure_user_exists(user_id)

        # Получаем группы целевого пользователя
        target_groups = await self._users_to_group_repo.user_groups(target_user_id)
        target_group_ids = {group.id for group, _ in target_groups}

        # Получаем группы текущего пользователя
        user_groups = await self._users_to_group_repo.user_groups(user_id)
        user_group_ids = {group.id for group, _ in user_groups}

        # Проверяем, есть ли общие группы
        common_groups = target_group_ids & user_group_ids
        if not common_groups:
            raise NotEnoughRights("Пользователи не состоят в общих группах")

        # Получаем события целевого пользователя, которые связаны с общими группами
        all_events = await self._event_repo.get_created_by_user(target_user_id)
        return [event for event in all_events if event.group_id in common_groups]
