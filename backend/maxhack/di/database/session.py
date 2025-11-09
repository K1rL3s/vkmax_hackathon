from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    close_all_sessions,
    create_async_engine,
)

from maxhack.config import Config
from maxhack.infra.database.transaction_manager import TransactionManager


class DBProvider(Provider):
    transaction_manager = provide(TransactionManager, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    async def engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        db_url = config.db.uri

        engine = create_async_engine(
            url=db_url,
            pool_size=50,
            pool_recycle=3600,
            pool_timeout=60,
            echo=False,
            max_overflow=20,
        )

        yield engine

        await engine.dispose(close=True)

    @provide(scope=Scope.APP)
    async def sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> AsyncIterable[async_sessionmaker[AsyncSession]]:
        sessionmaker = async_sessionmaker(
            bind=engine,
            autoflush=False,
            future=True,
            expire_on_commit=False,
        )
        yield sessionmaker
        await close_all_sessions()

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            try:
                yield session
            except:
                await session.rollback()
                raise
            else:
                await session.commit()
