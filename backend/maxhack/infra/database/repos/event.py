import logging
from typing import Any

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.exceptions import MaxHackError
from maxhack.core.ids import EventId, EventNotifyId, GroupId, TagId, UserId
from maxhack.infra.database.models import (
    EventModel,
    EventNotifyModel,
    RespondModel,
    TagModel,
    TagsToEvents,
    UserModel,
    UsersToEvents,
    UsersToTagsModel,
)
from maxhack.infra.database.repos.base import BaseAlchemyRepo

logger = logging.getLogger(__name__)


class EventRepo(BaseAlchemyRepo):
    async def get_by_id(self, event_id: EventId) -> EventModel | None:
        stmt = select(EventModel).where(
            EventModel.id == event_id,
            EventModel.is_not_deleted,
        )
        return await self._session.scalar(stmt)

    async def create(
        self,
        title: str,
        description: str | None,
        cron: str,
        is_cycle: bool,
        type: str,
        creator_id: UserId,
        group_id: GroupId,
        timezone: int = 0,
    ) -> EventModel:
        event = EventModel(
            title=title,
            description=description,
            cron=cron,
            is_cycle=is_cycle,
            type=type,
            creator_id=creator_id,
            group_id=group_id,
            timezone=timezone,
        )
        try:
            self._session.add(event)
            await self._session.flush()
            await self._session.refresh(event)
        except (ProgrammingError, IntegrityError) as e:
            raise MaxHackError from e

        return event

    async def update(self, event_id: EventId, **values: Any) -> EventModel | None:
        stmt = (
            update(EventModel)
            .where(
                EventModel.id == event_id,
                EventModel.is_not_deleted,
            )
            .values(**values)
            .returning(EventModel)
        )
        try:
            event = await self._session.scalar(stmt)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            logger.exception(str(e))
            raise RuntimeError from e

        return event

    async def delete(self, event_id: EventId) -> bool:
        update_tags_stmt = (
            update(TagsToEvents)
            .where(TagsToEvents.event_id == event_id)
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_tags_stmt)

        update_users_stmt = (
            update(UsersToEvents)
            .where(UsersToEvents.event_id == event_id)
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_users_stmt)

        update_notifies_stmt = (
            update(EventNotifyModel)
            .where(EventNotifyModel.event_id == event_id)
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_notifies_stmt)

        update_responds_stmt = (
            update(RespondModel)
            .where(RespondModel.event_id == event_id)
            .values(deleted_at=func.now())
        )
        await self._session.execute(update_responds_stmt)

        stmt = (
            update(EventModel)
            .where(
                EventModel.id == event_id,
                EventModel.is_not_deleted,
            )
            .values(deleted_at=func.now())
            .returning(EventModel)
        )
        result = await self._session.scalar(stmt)

        return bool(result)

    async def get_by_group(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .join(UsersToEvents, UsersToEvents.event_id == EventModel.id)
            .where(
                EventModel.group_id == group_id,
                UsersToEvents.user_id == user_id,
                EventModel.is_not_deleted,
            )
            .order_by(EventModel.created_at.desc())
        )
        return list(await self._session.execute(stmt))

    async def get_by_user(
        self,
        user_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .join(
                UsersToEvents,
                and_(
                    UsersToEvents.event_id == EventModel.id,
                    UsersToEvents.user_id == user_id,
                    UsersToEvents.is_not_deleted,
                ),
            )
            .where(EventModel.is_not_deleted)
        )

        if tag_ids:
            events_with_tags_subquery = (
                select(TagsToEvents.event_id)
                .where(
                    TagsToEvents.tag_id.in_(tag_ids),
                    TagsToEvents.is_not_deleted,
                )
                .scalar_subquery()
            )
            stmt = stmt.where(EventModel.id.in_(events_with_tags_subquery))

        stmt = stmt.order_by(EventModel.created_at.desc())

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_created_by_user(
        self,
        user_id: UserId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .where(
                EventModel.creator_id == user_id,
                EventModel.is_not_deleted,
            )
            .order_by(EventModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(await self._session.execute(stmt))

    async def add_tag(
        self,
        event_id: EventId,
        tag_ids: list[TagId],
    ) -> list[TagsToEvents]:
        relations = []

        for tag_id_item in tag_ids:
            relation = TagsToEvents(event_id=event_id, tag_id=tag_id_item)
            relations.append(relation)

        try:
            self._session.add_all(relations)
            await self._session.flush()

            for relation in relations:
                await self._session.refresh(relation)

        except (ProgrammingError, IntegrityError) as e:
            await self._session.rollback()
            raise RuntimeError(f"Failed to add tags to event: {e}") from e

        return relations

    async def remove_tag(self, event_id: EventId, tag_id: TagId) -> bool:
        stmt = (
            delete(TagsToEvents)
            .where(
                TagsToEvents.event_id == event_id,
                TagsToEvents.tag_id == tag_id,
            )
            .returning(TagsToEvents)
        )
        result = await self._session.scalar(stmt)
        await self._session.flush()
        return bool(result)

    async def get_event_tags(self, event_id: EventId) -> list[TagId]:
        stmt = select(TagsToEvents.tag_id).where(
            TagsToEvents.event_id == event_id,
            TagsToEvents.is_not_deleted,
        )
        return list(await self._session.execute(stmt))

    async def add_user(
        self,
        event_id: EventId,
        user_ids: list[UserId],
    ) -> list[UsersToEvents]:
        relations = [
            UsersToEvents(event_id=event_id, user_id=user_id) for user_id in user_ids
        ]

        if not relations:
            return []

        try:
            self._session.add_all(relations)
            await self._session.flush()

            for relation in relations:
                await self._session.refresh(relation)

        except (ProgrammingError, IntegrityError) as e:
            await self._session.rollback()
            raise RuntimeError(f"Failed to add users to event: {e}") from e

        return relations

    async def remove_user(self, event_id: EventId, user_id: UserId) -> bool:
        stmt = (
            update(UsersToEvents)
            .where(
                UsersToEvents.event_id == event_id,
                UsersToEvents.user_id == user_id,
                UsersToEvents.is_not_deleted,
            )
            .values(deleted_at=func.now())
            .returning(UsersToEvents)
        )
        result = await self._session.scalar(stmt)
        await self._session.flush()
        return bool(result)

    async def get_event_users(self, event_id: EventId) -> list[UserModel]:
        stmt = (
            select(UserModel)
            .join(UsersToEvents)
            .where(
                UsersToEvents.event_id == event_id,
                UsersToEvents.is_not_deleted,
            )
        )
        event_users = list(await self._session.scalars(stmt))

        stmt = (
            select(UserModel)
            .join(UsersToTagsModel)
            .join(TagModel)
            .join(TagsToEvents)
            .where(
                TagsToEvents.event_id == event_id,
                UsersToTagsModel.is_not_deleted,
                TagModel.is_not_deleted,
                TagsToEvents.is_not_deleted,
            )
        )
        tag_users = list(await self._session.scalars(stmt))

        result = []
        ids = set()
        for user in event_users + tag_users:
            if user.id not in ids:
                ids.add(user.id)
                result.append(user)

        return result

    async def check_user_in_event(
        self,
        event_id: EventId,
        user_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> bool:
        stmt = (
            select(UsersToEvents)
            .join(EventModel, EventModel.id == UsersToEvents.event_id)
            .where(
                UsersToEvents.event_id == event_id,
                UsersToEvents.user_id == user_id,
                UsersToEvents.is_not_deleted,
                EventModel.is_not_deleted,
            )
        )

        if tag_ids:
            events_with_tags_subquery = (
                select(TagsToEvents.event_id)
                .where(
                    TagsToEvents.event_id == event_id,
                    TagsToEvents.tag_id.in_(tag_ids),
                    TagsToEvents.is_not_deleted,
                )
                .scalar_subquery()
            )
            stmt = stmt.where(EventModel.id.in_(events_with_tags_subquery))

        result = await self._session.scalar(stmt)
        return result is not None

    async def list_user_events(
        self,
        group_id: GroupId,
        user_id: UserId,
        tag_ids: list[TagId] | None = None,
    ) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .join(UsersToEvents, EventModel.id == UsersToEvents.event_id)
            .where(
                EventModel.group_id == group_id,
                UsersToEvents.user_id == user_id,
                EventModel.is_not_deleted,
                UsersToEvents.is_not_deleted,
            )
        )
        if tag_ids:
            events_with_tags_subquery = (
                select(TagsToEvents.event_id)
                .where(
                    TagsToEvents.tag_id.in_(tag_ids),
                    TagsToEvents.is_not_deleted,
                )
                .scalar_subquery()
            )
            stmt = stmt.where(EventModel.id.in_(events_with_tags_subquery))

        return list(await self._session.scalars(stmt))

    async def create_notify(
        self,
        event_id: EventId,
        minutes_before: list[int],
    ) -> list[EventNotifyModel]:
        minutes_before.append(0)
        minutes_before = set(minutes_before)
        notifies = [
            EventNotifyModel(event_id=event_id, minutes_before=minutes)
            for minutes in minutes_before
        ]
        try:
            self._session.add_all(notifies)
            await self._session.flush()
            for notify in notifies:
                await self._session.refresh(notify)
        except (ProgrammingError, IntegrityError) as e:
            raise RuntimeError from e

        return notifies

    async def get_notify_by_id(
        self,
        event_notify_id: EventNotifyId,
    ) -> EventNotifyModel | None:
        stmt = select(EventNotifyModel).where(
            EventNotifyModel.id == event_notify_id,
            EventNotifyModel.is_not_deleted,
        )
        return await self._session.scalar(stmt)

    async def get_notify_by_date_interval(
        self,
    ) -> list[tuple[EventNotifyModel, EventModel]]:
        stmt = (
            select(EventNotifyModel, EventModel)
            .join(EventModel)
            .where(EventModel.event_happened == False)
        )
        return list(await self._session.execute(stmt))
