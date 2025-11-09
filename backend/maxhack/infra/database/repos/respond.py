from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError

from maxhack.core.ids import EventId, RespondId, UserId
from maxhack.infra.database.models import RespondModel
from maxhack.infra.database.repos.base import BaseAlchemyRepo


class RespondRepo(BaseAlchemyRepo):
    async def get_by_id(self, respond_id: RespondId) -> RespondModel | None:
        stmt = select(RespondModel).where(
            RespondModel.id == respond_id,
            RespondModel.deleted_at.is_(None),
        )
        return await self._session.scalar(stmt)

    async def create(
        self,
        user_ids: list[UserId],
        event_id: EventId,
        status: str,
    ) -> list[RespondModel]:
        events = [
            RespondModel(user_id=creator_id, event_id=event_id, status=status)
            for creator_id in user_ids
        ]

        if not events:
            return []

        try:

            self._session.add_all(events)
            await self._session.flush()
            for event in events:
                await self._session.refresh(event)

        except (ProgrammingError, IntegrityError) as e:
            await self._session.rollback()
            raise RuntimeError(f"Ошибка при создании respond: {e}") from e

        return events

    async def update(self, event_id: EventId, **values: Any) -> RespondModel | None:
        stmt = (
            update(RespondModel)
            .where(
                RespondModel.id == event_id,
                RespondModel.deleted_at.is_(None),
            )
            .values(**values)
            .returning(RespondModel)
        )
        try:
            event = await self._session.scalar(stmt)
            await self._session.flush()
        except (ProgrammingError, IntegrityError) as e:
            raise RuntimeError from e

        return event

    async def delete(self, event_id: EventId) -> bool:
        stmt = (
            update(RespondModel)
            .where(
                RespondModel.id == event_id,
                RespondModel.deleted_at.is_(None),
            )
            .values(deleted_at=func.now())
            .returning(RespondModel)
        )
        result = await self._session.scalar(stmt)
        await self._session.flush()
        return bool(result)
