from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class TransactionManager:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[None]:
        if self._session.in_transaction():
            yield None
            await self._commit()
        else:
            async with self._session.begin():
                yield None
                await self._commit()

    @asynccontextmanager
    async def begin_nested(self) -> AsyncIterator[None]:
        if self._session.in_nested_transaction():
            yield None
        else:
            async with self._session.begin_nested():
                yield None

    async def _commit(self) -> None:
        await self._session.commit()
