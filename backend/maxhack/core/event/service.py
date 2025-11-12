from datetime import datetime

from maxhack.core.event.models import EventCreate, EventUpdate
from maxhack.core.exceptions import (
    EventNotFound,
    GroupNotFound,
    InvalidValue,
    NotEnoughRights,
    TagNotFound,
    UserNotFound,
)
from maxhack.core.group.service import GroupService
from maxhack.core.ids import EventId, GroupId, TagId, UserId
from maxhack.core.responds.service import RespondService
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID
from maxhack.infra.database.models import (
    EventModel,
    TagModel,
    UserModel,
    UsersToGroupsModel,
)
from maxhack.infra.database.repos.event import EventRepo
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.tag import TagRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo
from maxhack.utils.utils import create_cron_expression


class EventService:
    def __init__(
        self,
        event_repo: EventRepo,
        tag_repo: TagRepo,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        events_repo: EventRepo,
        users_to_group_repo: UsersToGroupsRepo,
        respond_service: RespondService,
        group_service: GroupService,
    ) -> None:
        self._event_repo = event_repo
        self._tag_repo = tag_repo
        self._group_repo = group_repo
        self._user_repo = user_repo
        self._users_to_group_repo = users_to_group_repo
        self._respond_service = respond_service
        self._group_service = group_service
        self._events_repo = events_repo

    async def _ensure_group_exists(self, group_id: GroupId | None) -> None:
        if group_id is None:
            return
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound

    async def _ensure_user_exists(self, user_id: UserId) -> UserModel:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound
        return user

    async def _ensure_event_exists(self, event_id: EventId) -> EventModel:
        event = await self._event_repo.get_by_id(event_id)
        if event is None:
            raise EventNotFound
        return event

    async def _ensure_tag_exists(self, tag_id: TagId) -> TagModel:
        tag = await self._tag_repo.get_by_id(tag_id)
        if tag is None:
            raise TagNotFound
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
        event_create_model: EventCreate,
    ) -> EventModel:
        creator = await self._ensure_user_exists(event_create_model.creator_id)

        is_cycle = any(event_create_model.to_dict().values())

        if event_create_model.group_id:
            group, role = await self._group_service.get_group(
                member_id=event_create_model.creator_id,
                group_id=event_create_model.group_id,
            )

            if role.id not in {CREATOR_ROLE_ID, EDITOR_ROLE_ID}:
                raise NotEnoughRights("Недостаточно прав для создания события в группе")

            event_create_model.timezone = group.timezone

        event = await self._event_repo.create(
            title=event_create_model.title,
            description=event_create_model.description,
            cron=event_create_model.cron.expression,
            is_cycle=is_cycle,
            type=event_create_model.type,
            creator_id=event_create_model.creator_id,
            group_id=event_create_model.group_id,
            timezone=event_create_model.timezone
            if event_create_model.timezone
            else creator.timezone,
        )
        await self.add_tag_to_event(
            event.id,
            event_create_model.tags_ids,
            user_id=creator.id,
        )
        await self.add_user_to_event(
            event.id,
            event_create_model.participants_ids,
            user_id=creator.id,
        )

        match event_create_model.type:
            case "event":
                if event_create_model.group_id:
                    for tid in event_create_model.tags_ids:
                        users = await self._tag_repo.list_tag_users(
                            group_id=event_create_model.group_id,
                            tag_id=tid,
                        )

                        event_create_model.participants_ids.extend(
                            [u.id for u, _ in users],
                        )

                    await self._respond_service.create(
                        user_ids=list(set(event_create_model.participants_ids)),
                        event_id=event.id,
                        status="mb",
                    )
            case _:
                ...

        await self._event_repo.create_notify(
            event_id=event.id,
            minutes_before=event_create_model.minutes_before,
        )

        return event

    async def update_event(
        self,
        event_id: EventId,
        user_id: UserId,
        event_update_model: EventUpdate,
    ) -> EventModel:
        event = await self._ensure_event_exists(event_id)

        if event.group_id:
            await self._ensure_membership_role(
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
                user_id=user_id,
                group_id=event.group_id,
            )
        elif event.creator_id != user_id:
            raise NotEnoughRights

        is_cycle = event.is_cycle
        if event_update_model.cron:
            is_cycle = any([event_update_model.cron.to_dict(exclude={"date"}).values()])

        updated_event = await self._event_repo.update(
            event_id,
            **event_update_model.to_dict(exclude_none=True),
            is_cycle=is_cycle,
        )
        if updated_event is None:
            raise EventNotFound

        return updated_event

    async def delete_event(self, event_id: EventId, user_id: UserId) -> None:
        event = await self._ensure_event_exists(event_id)

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
            raise GroupNotFound

    async def add_tag_to_event(
        self,
        event_id: EventId,
        tag_ids: list[TagId],
        user_id: UserId,
    ) -> None:
        event = await self._ensure_event_exists(event_id)

        if not tag_ids:
            return

        tags = [await self._ensure_tag_exists(tag_id) for tag_id in tag_ids]

        if event.group_id is not None:
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
            )
            invalid_tags = [tag.id for tag in tags if tag.group_id != event.group_id]
            if invalid_tags:
                raise InvalidValue(
                    f"Теги не принадлежат группе события: {invalid_tags}",
                )
        elif event.creator_id != user_id:
            raise NotEnoughRights("Недостаточно прав для добавления тега")

        event_tags = await self._event_repo.get_event_tags(event_id)
        new_tag_ids = [tag_id for tag_id in tag_ids if tag_id not in event_tags]

        if not new_tag_ids:
            raise InvalidValue("Все указанные теги уже добавлены к событию")

        await self._event_repo.add_tag(event_id, new_tag_ids)

        if event.type == "event":
            user_ids = []
            for tag_id in new_tag_ids:
                user, _ = await self._tag_repo.list_tag_users(
                    group_id=event.group_id,
                    tag_id=tag_id,
                )
                user_ids.append(user.id)
            await self._respond_service.create(user_ids, event.id, status="mb")

    async def add_user_to_event(
        self,
        event_id: EventId,
        target_user_ids: list[UserId],
        user_id: UserId,
    ) -> None:
        if not target_user_ids:
            return

        event = await self._ensure_event_exists(event_id)

        for target_user_id in target_user_ids:
            await self._ensure_user_exists(target_user_id)

        if event.group_id is not None:
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles={CREATOR_ROLE_ID, EDITOR_ROLE_ID},
            )

            for target_user_id in target_user_ids:
                target_membership = await self._users_to_group_repo.get_membership(
                    user_id=target_user_id,
                    group_id=event.group_id,
                )
                if target_membership is None:
                    raise InvalidValue(
                        f"Пользователь {target_user_id} не состоит в группе события",
                    )

        elif event.creator_id != user_id:
            raise NotEnoughRights("Недостаточно прав для добавления пользователя")

        existing_users = []
        for target_user_id in target_user_ids:
            is_in_event = await self._event_repo.check_user_in_event(
                event_id,
                target_user_id,
            )
            if is_in_event:
                existing_users.append(target_user_id)

        if existing_users:
            raise InvalidValue(
                f"Пользователи уже добавлены к событию: {existing_users}",
            )

        await self._event_repo.add_user(event_id, target_user_ids)

        if event.type == "event":
            await self._respond_service.create(target_user_ids, event.id, status="mb")

    async def get_group_events(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> list[EventModel]:
        await self._ensure_group_exists(group_id)

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

        target_groups = await self._users_to_group_repo.user_groups(target_user_id)
        target_group_ids = {group.id for group, _ in target_groups}

        user_groups = await self._users_to_group_repo.user_groups(user_id)
        user_group_ids = {group.id for group, _ in user_groups}

        common_groups = target_group_ids & user_group_ids
        if not common_groups:
            raise NotEnoughRights("Пользователи не состоят в общих группах")

        all_events = await self._event_repo.get_created_by_user(target_user_id)
        return [event for event in all_events if event.group_id in common_groups]

    async def list_user_events(
        self,
        group_id: GroupId,
        user_id: UserId,
        master_id: UserId,
    ) -> list[EventModel]:
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

        return await self._events_repo.list_user_events(group_id, user_id)
