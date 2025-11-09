from typing import Any

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.ids import EventId, GroupId, TagId, UserId
from maxhack.infra.database.models import (
    EventModel,
    TagsToEvents,
    UsersToEvents,
)
from maxhack.infra.database.repos.base import BaseAlchemyRepo


class EventRepo(BaseAlchemyRepo):
    async def get_by_id(self, event_id: EventId) -> EventModel | None:
        stmt = select(EventModel).where(
            EventModel.id == event_id,
            EventModel.deleted_at.is_(None),
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
        group_id: GroupId | None,
    ) -> EventModel:
        event = EventModel(
            title=title,
            description=description,
            cron=cron,
            is_cycle=is_cycle,
            type=type,
            creator_id=creator_id,
            group_id=group_id,
        )
        try:
            self._session.add(event)
            await self._session.flush()
            await self._session.refresh(event)
        except (ProgrammingError, IntegrityError) as e:
            raise RuntimeError from e

        return event

    async def update(self, event_id: EventId, **values: Any) -> EventModel | None:
        stmt = (
            update(EventModel)
            .where(
                EventModel.id == event_id,
                EventModel.deleted_at.is_(None),
            )
            .values(**values)
            .returning(EventModel)
        )
        try:
            event = await self._session.scalar(stmt)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise RuntimeError from e

        return event

    async def delete(self, event_id: EventId) -> bool:
        stmt = (
            update(EventModel)
            .where(
                EventModel.id == event_id,
                EventModel.deleted_at.is_(None),
            )
            .values(deleted_at=func.now())
            .returning(EventModel)
        )
        result = await self._session.scalar(stmt)
        await self._session.flush()
        return bool(result)

    async def get_by_group(
        self,
        group_id: GroupId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .where(
                EventModel.group_id == group_id,
                EventModel.deleted_at.is_(None),
            )
            .order_by(EventModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: UserId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .join(
                UsersToEvents,
                and_(
                    UsersToEvents.event_id == EventModel.id,
                    UsersToEvents.user_id == user_id,
                    UsersToEvents.deleted_at.is_(None),
                ),
            )
            .where(EventModel.deleted_at.is_(None))
            .order_by(EventModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
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
                EventModel.deleted_at.is_(None),
            )
            .order_by(EventModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

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
            TagsToEvents.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

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
                UsersToEvents.deleted_at.is_(None),
            )
            .values(deleted_at=func.now())
            .returning(UsersToEvents)
        )
        result = await self._session.scalar(stmt)
        await self._session.flush()
        return bool(result)

    async def get_event_users(self, event_id: EventId) -> list[UserId]:
        stmt = select(UsersToEvents.user_id).where(
            UsersToEvents.event_id == event_id,
            UsersToEvents.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def check_user_in_event(
        self,
        event_id: EventId,
        user_id: UserId,
    ) -> bool:
        stmt = select(UsersToEvents).where(
            UsersToEvents.event_id == event_id,
            UsersToEvents.user_id == user_id,
            UsersToEvents.deleted_at.is_(None),
        )
        result = await self._session.scalar(stmt)
        return result is not None
