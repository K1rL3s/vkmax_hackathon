from datetime import datetime, timedelta

import pycron
from redis.asyncio import Redis

from maxhack.core.event.models import EventCreate, EventUpdate
from maxhack.core.exceptions import (
    EventNotFound,
    GroupNotFound,
    InvalidValue,
    NotEnoughRights,
)
from maxhack.core.group.service import GroupService
from maxhack.core.ids import EventId, GroupId, TagId, UserId
from maxhack.core.responds.service import RespondService
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.service import BaseService
from maxhack.core.tag.service import TagService
from maxhack.core.utils.datehelp import datetime_now
from maxhack.database.models import (
    EventModel,
    EventNotifyModel,
    GroupModel,
    RespondModel,
    UserModel,
    UsersToGroupsModel,
)
from maxhack.database.repos.event import EventRepo
from maxhack.database.repos.group import GroupRepo
from maxhack.database.repos.invite import InviteRepo
from maxhack.database.repos.respond import RespondRepo
from maxhack.database.repos.role import RoleRepo
from maxhack.database.repos.tag import TagRepo
from maxhack.database.repos.user import UserRepo
from maxhack.database.repos.users_to_groups import UsersToGroupsRepo
from maxhack.logger.setup import get_logger

logger = get_logger(__name__)


class EventService(BaseService):
    def __init__(
        self,
        event_repo: EventRepo,
        tag_repo: TagRepo,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        users_to_groups_repo: UsersToGroupsRepo,
        respond_repo: RespondRepo,
        invite_repo: InviteRepo,
        respond_service: RespondService,
        group_service: GroupService,
        role_repo: RoleRepo,
        redis: Redis,
        tag_service: TagService,
    ) -> None:
        super().__init__(
            event_repo=event_repo,
            tag_repo=tag_repo,
            group_repo=group_repo,
            user_repo=user_repo,
            users_to_groups_repo=users_to_groups_repo,
            respond_repo=respond_repo,
            invite_repo=invite_repo,
            role_repo=role_repo,
        )
        self._respond_service = respond_service
        self._group_service = group_service
        self._redis = redis
        self._tag_service = tag_service

    async def get_event(self, event_id: EventId, user_id: UserId) -> EventModel:
        logger.debug(f"Getting event {event_id} for user {user_id}")
        event = await self._ensure_event_exists(event_id)

        if event.group_id is not None:
            logger.debug(f"Event {event_id} is in group {event.group_id}")
            membership = await self._users_to_groups_repo.get_membership(
                user_id=user_id,
                group_id=event.group_id,
            )
            if membership is None:
                logger.debug(
                    f"User {user_id} is not a member of group {event.group_id}",
                )
                is_in_event = await self._event_repo.check_user_in_event(
                    event_id,
                    user_id,
                )
                if not is_in_event and event.creator_id != user_id:
                    logger.warning(
                        f"User {user_id} has no rights to view event {event_id}",
                    )
                    raise NotEnoughRights
        elif event.creator_id != user_id:
            logger.debug(f"Event {event_id} is not in a group")
            is_in_event = await self._event_repo.check_user_in_event(event_id, user_id)
            if not is_in_event:
                logger.warning(f"User {user_id} has no rights to view event {event_id}")
                raise NotEnoughRights

        logger.info(f"Event {event_id} successfully retrieved for user {user_id}")
        return event

    async def create_event(
        self,
        event_create_scheme: EventCreate,
    ) -> tuple[EventModel, list[EventNotifyModel]]:
        logger.debug(f"Creating event with data: {event_create_scheme}")
        creator = await self._ensure_user_exists(event_create_scheme.creator_id)

        is_cycle = event_create_scheme.cron.is_cycle

        if event_create_scheme.group_id:
            logger.debug(f"Event is in group {event_create_scheme.group_id}")
            group, role = await self._group_service.get_group(
                member_id=event_create_scheme.creator_id,
                group_id=event_create_scheme.group_id,
            )

            if role.id not in {CREATOR_ROLE_ID, EDITOR_ROLE_ID}:
                logger.warning(
                    f"User {creator.id} has no rights to create event in group {group.id}",
                )
                raise NotEnoughRights

            event_create_scheme.timezone = group.timezone

        event = await self._event_repo.create(
            title=event_create_scheme.title,
            description=event_create_scheme.description,
            cron=event_create_scheme.cron.expression,
            is_cycle=is_cycle,
            type=event_create_scheme.type,
            creator_id=event_create_scheme.creator_id,
            group_id=event_create_scheme.group_id,
            duration=event_create_scheme.duration,
        )
        logger.info(f"Event {event.id} created successfully")
        await self.add_tag_to_event(
            event.id,
            event_create_scheme.tags_ids,
            user_id=creator.id,
        )
        await self.add_user_to_event(
            event.id,
            event_create_scheme.participants_ids,
            user_id=creator.id,
        )

        if event_create_scheme.type == "event":
            for tid in event_create_scheme.tags_ids:
                users = await self._tag_repo.list_tag_users(
                    group_id=event_create_scheme.group_id,
                    tag_id=tid,
                )
                event_create_scheme.participants_ids.extend(
                    [u.id for u, _ in users],
                )

        notifies = await self._event_repo.create_notify(
            event_id=event.id,
            minutes_before=event_create_scheme.minutes_before,
        )
        logger.debug(f"Created {len(notifies)} notifies for event {event.id}")

        return event, notifies

    async def update_event(
        self,
        event_id: EventId,
        user_id: UserId,
        event_update_model: EventUpdate,
    ) -> EventModel:
        logger.debug(
            f"Updating event {event_id} by user {user_id} with data: {event_update_model}",
        )
        event = await self._ensure_event_exists(event_id)

        if event.group_id:
            logger.debug(f"Event {event_id} is in group {event.group_id}")
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
            )
        elif event.creator_id != user_id:
            logger.warning(f"User {user_id} has no rights to update event {event_id}")
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
            logger.error(f"Event {event_id} not found for update")
            raise EventNotFound

        logger.info(f"Event {event_id} updated successfully")
        return updated_event

    async def delete_event(self, event_id: EventId, user_id: UserId) -> None:
        logger.debug(f"Deleting event {event_id} by user {user_id}")
        event = await self._ensure_event_exists(event_id)

        if event.group_id is not None:
            logger.debug(f"Event {event_id} is in group {event.group_id}")
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
            )
        elif event.creator_id != user_id:
            logger.warning(f"User {user_id} has no rights to delete event {event_id}")
            raise NotEnoughRights

        success = await self._event_repo.delete(event_id)
        if not success:
            logger.error(f"Event {event_id} not found for deletion")
            raise GroupNotFound

        logger.info(f"Event {event_id} deleted successfully")

    async def add_tag_to_event(
        self,
        event_id: EventId,
        tag_ids: list[TagId],
        user_id: UserId,
    ) -> None:
        logger.debug(f"Adding tags {tag_ids} to event {event_id} by user {user_id}")
        event = await self._ensure_event_exists(event_id)

        if not tag_ids:
            logger.debug("No tags to add")
            return

        tags = [await self._ensure_tag_exists(tag_id) for tag_id in tag_ids]

        if event.group_id is not None:
            logger.debug(f"Event {event_id} is in group {event.group_id}")
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
            )
            invalid_tags = [tag.id for tag in tags if tag.group_id != event.group_id]
            if invalid_tags:
                logger.warning(f"Invalid tags {invalid_tags} for event {event_id}")
                raise InvalidValue(
                    f"Теги не принадлежат группе события: {invalid_tags}",
                )
        elif event.creator_id != user_id:
            logger.warning(
                f"User {user_id} has no rights to add tags to event {event_id}",
            )
            raise NotEnoughRights

        event_tags = await self._event_repo.get_event_tags(event_id)
        new_tag_ids = [tag_id for tag_id in tag_ids if tag_id not in event_tags]

        if not new_tag_ids:
            logger.warning(f"All tags {tag_ids} already added to event {event_id}")
            raise InvalidValue("Все указанные теги уже добавлены к событию")

        await self._event_repo.add_tag(event_id, new_tag_ids)
        logger.info(f"Tags {new_tag_ids} added to event {event_id}")

        if event.type == "event":
            user_ids = []
            for tag_id in new_tag_ids:
                users = await self._tag_repo.list_tag_users(
                    group_id=event.group_id,
                    tag_id=tag_id,
                )
                for user, _ in users:
                    user_ids.append(user.id)
            await self._respond_service.create(user_ids, event.id, status="mb")
            logger.debug(f"Created responds for users {user_ids} for event {event.id}")

    async def add_user_to_event(
        self,
        event_id: EventId,
        target_user_ids: list[UserId],
        user_id: UserId,
    ) -> None:
        logger.debug(
            f"Adding users {target_user_ids} to event {event_id} by user {user_id}",
        )
        if not target_user_ids:
            logger.debug("No users to add")
            return

        event = await self._ensure_event_exists(event_id)

        for target_user_id in target_user_ids:
            await self._ensure_user_exists(target_user_id)

        if event.group_id is not None:
            logger.debug(f"Event {event_id} is in group {event.group_id}")
            await self._ensure_membership_role(
                user_id=user_id,
                group_id=event.group_id,
                allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
            )

            for target_user_id in target_user_ids:
                target_membership = await self._users_to_groups_repo.get_membership(
                    user_id=target_user_id,
                    group_id=event.group_id,
                )
                if target_membership is None:
                    logger.warning(
                        f"User {target_user_id} is not in group {event.group_id}",
                    )
                    raise InvalidValue(
                        f"Пользователь {target_user_id} не состоит в группе события",
                    )

        elif event.creator_id != user_id:
            logger.warning(
                f"User {user_id} has no rights to add users to event {event_id}",
            )
            raise NotEnoughRights

        existing_users = []
        for target_user_id in target_user_ids:
            is_in_event = await self._event_repo.check_user_in_event(
                event_id,
                target_user_id,
            )
            if is_in_event:
                existing_users.append(target_user_id)

        if existing_users:
            logger.warning(f"Users {existing_users} already added to event {event_id}")
            raise InvalidValue(
                f"Пользователи уже добавлены к событию: {existing_users}",
            )

        await self._event_repo.add_user(event_id, target_user_ids)
        logger.info(f"Users {target_user_ids} added to event {event_id}")

        if event.type == "event":
            await self._respond_service.create(target_user_ids, event.id, status="mb")
            logger.debug(
                f"Created responds for users {target_user_ids} for event {event_id}",
            )

    async def get_group_events(
        self,
        group_id: GroupId,
        user_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> list[tuple[EventModel, RespondModel | None]]:
        logger.debug(f"Getting events for group {group_id} for user {user_id}")
        await self._ensure_group_exists(group_id)

        membership = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None:
            logger.warning(f"User {user_id} is not in group {group_id}")
            raise NotEnoughRights

        if membership.role_id in {CREATOR_ROLE_ID, EDITOR_ROLE_ID}:
            events = await self._event_repo.get_by_group_id(group_id, tag_ids)
            logger.info(
                f"Found {len(events)} events for group {group_id} (all events for role {membership.role_id})",
            )
        else:
            events = await self._event_repo.get_by_group(group_id, user_id, tag_ids)
            logger.info(
                f"Found {len(events)} events for group {group_id} for user {user_id}",
            )

        result: list[tuple[EventModel, RespondModel | None]] = []
        for event in events:
            respond = await self._respond_repo.get_user_respond(
                event_id=event.id,
                user_id=user_id,
            )
            result.append((event, respond))

        return result

    async def get_user_events(
        self,
        user_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> list[EventModel]:
        logger.debug(f"Getting events for user {user_id} with tags {tag_ids}")
        await self._ensure_user_exists(user_id)
        events = await self._event_repo.get_created_by_user(user_id, tag_ids=tag_ids)
        logger.info(f"Found {len(events)} events for user {user_id}")
        return events

    async def get_other_user_events(
        self,
        target_user_id: UserId,
        user_id: UserId,
    ) -> list[EventModel]:
        # TODO: Удалить или использовать
        logger.debug(
            f"Getting events for user {target_user_id} requested by user {user_id}",
        )
        await self._ensure_user_exists(target_user_id)

        target_groups = await self._users_to_groups_repo.user_groups(target_user_id)
        target_group_ids = {group.id for group, _ in target_groups}
        logger.debug(f"User {target_user_id} is in groups {target_group_ids}")

        user_groups = await self._users_to_groups_repo.user_groups(user_id)
        user_group_ids = {group.id for group, _ in user_groups}
        logger.debug(f"User {user_id} is in groups {user_group_ids}")

        common_groups = target_group_ids & user_group_ids
        if not common_groups:
            logger.warning(
                f"Users {user_id} and {target_user_id} have no common groups",
            )
            raise NotEnoughRights
        logger.debug(
            f"Common groups for users {user_id} and {target_user_id}: {common_groups}",
        )

        all_events = await self._event_repo.get_created_by_user(target_user_id)
        events = [event for event in all_events if event.group_id in common_groups]
        logger.info(
            f"Found {len(events)} events for user {target_user_id} in common groups",
        )
        return events

    async def list_user_events(
        self,
        group_id: GroupId,
        user_id: UserId,
        master_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> list[EventModel]:
        logger.debug(
            f"Listing events for user {user_id} in group {group_id} requested by user {master_id} with tags {tag_ids}",
        )
        await self._ensure_group_exists(group_id)

        await self._ensure_membership_role(
            user_id=master_id,
            group_id=group_id,
        )

        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
        )

        events = await self._event_repo.list_user_events(group_id, user_id, tag_ids)
        logger.info(
            f"Found {len(events)} events for user {user_id} in group {group_id}",
        )
        return events

    async def get_notify_by_date_interval(
        self,
    ) -> list[tuple[list[tuple[UserModel, UsersToGroupsModel | None]], EventModel]]:
        logger.debug("Getting notifications by date interval")
        time_now = datetime_now()
        last_start_str = await self._redis.get("last_start")
        if last_start_str:
            last_start = datetime.fromisoformat(last_start_str.decode())
            logger.debug(f"Last start time found in redis: {last_start}")
        else:
            last_start = time_now
            logger.debug("Last start time not found in redis, using current time")

        events_with_notifies = await self._event_repo.get_notifies()
        logger.debug(f"Found {len(events_with_notifies)} events with notifies")
        matching_notify: list[
            tuple[list[tuple[UserModel, UsersToGroupsModel | None]], EventModel]
        ] = []

        for event_notify, event in events_with_notifies:
            try:
                # Для уведомлений проверяем интервал: от (last_start - minutes_before) до time_now
                # Это позволяет отправить уведомление, если событие произойдет между last_start и time_now
                check_time = last_start - timedelta(minutes=event_notify.minutes_before)
                if pycron.has_been(event.cron, since=check_time, dt=time_now):
                    logger.debug(f"Event {event.id} matches cron expression")
                    # Помечаем событие как случившееся, если оно не повторяющееся и уведомление за 0 минут
                    if not event.is_cycle and event_notify.minutes_before == 0:
                        # Проверяем, что событие действительно произошло между last_start и time_now
                        if pycron.has_been(event.cron, since=last_start, dt=time_now):
                            await self._event_repo.update(event.id, event_happened=True)
                            logger.debug(f"Event {event.id} marked as happened")

                    users = await self._event_repo.get_event_users(event.id)
                    logger.debug(f"Found {len(users)} users for event {event.id}")
                    users_with_group_info: list[
                        tuple[UserModel, UsersToGroupsModel | None]
                    ] = []

                    for user in users:
                        membership: UsersToGroupsModel | None = None
                        if event.group_id:
                            membership = (
                                await self._users_to_groups_repo.get_membership(
                                    user_id=user.id,
                                    group_id=event.group_id,
                                )
                            )
                        users_with_group_info.append((user, membership))

                    matching_notify.append((users_with_group_info, event))
                    logger.debug(f"Event {event.id} added to matching notifications")

            except Exception as e:
                logger.error(
                    f"Error processing event {event.id} with cron '{event.cron}': {e}",
                )
                continue

        # Сохраняем time_now в redis как новый last_start только после обработки всех событий
        await self._redis.set("last_start", time_now.isoformat())
        logger.debug(f"New last start time set to redis: {time_now}")

        logger.info(f"Found {len(matching_notify)} matching notifications")
        return matching_notify

    async def get_user_events_all_groups_for_export(
        self,
        user_id: UserId,
    ) -> tuple[list[EventModel], dict[GroupId, GroupModel]]:
        """Получает все события пользователя из всех его групп для экспорта.

        Returns:
            tuple[list[EventModel], dict[GroupId, GroupModel]]: События и словарь групп
        """
        logger.debug(f"Getting all user events from all groups for export for user {user_id}")
        await self._ensure_user_exists(user_id)

        # Получаем все группы пользователя
        user_groups = await self._users_to_groups_repo.user_groups(user_id)

        # Собираем все события из всех групп, где пользователь участвует
        all_events: list[EventModel] = []
        groups_dict: dict[GroupId, GroupModel] = {}

        for group, _ in user_groups:
            groups_dict[group.id] = group
            # Получаем события пользователя в этой группе
            events = await self._event_repo.list_user_events(
                group_id=group.id,
                user_id=user_id,
                tag_ids=None,
            )
            all_events.extend(events)

        logger.info(
            f"Found {len(all_events)} events for user {user_id} in {len(groups_dict)} groups",
        )
        return all_events, groups_dict

    async def get_user_events_in_group_for_export(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> tuple[list[EventModel], dict[GroupId, GroupModel]]:
        """Получает все события пользователя в рамках одной группы для экспорта.

        Returns:
            tuple[list[EventModel], dict[GroupId, GroupModel]]: События и словарь с одной группой
        """
        logger.debug(
            f"Getting user events in group {group_id} for export for user {user_id}",
        )
        await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(user_id=user_id, group_id=group_id)

        # Получаем события пользователя в группе
        events = await self._event_repo.list_user_events(
            group_id=group_id,
            user_id=user_id,
            tag_ids=None,
        )

        # Получаем информацию о группе
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            logger.error(f"Group {group_id} not found")
            raise GroupNotFound

        groups_dict = {group_id: group}

        logger.info(
            f"Found {len(events)} events for user {user_id} in group {group_id}",
        )
        return events, groups_dict

    async def get_all_group_events_for_export(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> tuple[list[EventModel], dict[GroupId, GroupModel]]:
        """Получает все события группы для экспорта. Доступно только для ролей 1 и 2.

        Returns:
            tuple[list[EventModel], dict[GroupId, GroupModel]]: События и словарь с одной группой
        """
        logger.debug(f"Getting all group events for export for group {group_id} by user {user_id}")
        await self._ensure_group_exists(group_id)

        # Проверяем права доступа
        membership = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None:
            logger.warning(f"User {user_id} is not in group {group_id}")
            raise NotEnoughRights

        # Проверяем, что пользователь имеет роль 1 или 2
        if membership.role_id not in {CREATOR_ROLE_ID, EDITOR_ROLE_ID}:
            logger.warning(
                f"User {user_id} with role {membership.role_id} has no rights to export all events from group {group_id}",
            )
            raise NotEnoughRights

        # Получаем все события группы
        events_with_responds = await self.get_group_events(
            group_id=group_id,
            user_id=user_id,
        )
        events = [event for event, _ in events_with_responds]

        # Получаем информацию о группе
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            logger.error(f"Group {group_id} not found")
            raise GroupNotFound

        groups_dict = {group_id: group}

        logger.info(f"Found {len(events)} events in group {group_id} for export")
        return events, groups_dict

    async def get_by_user(
        self,
        user_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> list[EventModel]:
        logger.debug(f"Getting events for user {user_id} with tags {tag_ids}")
        if tag_ids:
            for tag_id in tag_ids:
                await self._tag_service._ensure_tag_exists(tag_id)
        events = await self._event_repo.get_by_user(user_id, tag_ids)
        logger.info(f"Found {len(events)} events for user {user_id}")
        return events
