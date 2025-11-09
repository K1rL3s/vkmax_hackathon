"""
Модуль для организации соединения с базой данных.
"""

# noinspection PyUnresolvedReferences

from maxhack.core.config import Config
from maxhack.infra.database.connection import async_session_factory
from maxhack.utils import json_serialization

# engine_params: dict[str, Any] = {"json_serializer": json_serialization.dumps}


# class AsyncDatabaseConnectionManager(_AsyncGeneratorContextManager[AsyncSession]):
#     """
#     Контекстный менеджер для получения соединения с БД.
#
#     Нужен для обхода мемоизации аргументов функции у dependency injector и позволяет подменять
#     настоящую бд на тестовую. В остальном **почти** ничем не отличается от обычного контекстного менеджера
#     (разве что чётко **завязан на DI;; и работает только после инициализации контейнера)
#     """
#
#     def __init__(
#         self,
#         async_db_session: Callable[[], AsyncGenerator[AsyncSession, None]] = Provide[
#             "_async_db_session"
#         ],
#     ):
#         self._creation_func = async_db_session
#
#         self.args: tuple[Any, ...] | None = None
#         self.kwds: dict[str, Any] | None = None
#         self.func: Callable[..., AsyncGenerator[Any, None]] | None = None
#
#     async def __aenter__(self) -> AsyncSession:
#         self.gen = self._creation_func()
#         return await super().__aenter__()
#
#     async def __aexit__(
#         self,
#         exc_type: type[BaseException] | None,
#         exc_val: BaseException | None,
#         exc_tb: TracebackType | None,
#     ) -> bool | None:
#         return await super().__aexit__(exc_type, exc_val, exc_tb)


# Теперь менеджеры нельзя использовать напрямую (за исключением нетестируемых CLI), используйте
# InfrastructureContainer.async_db_session_manager
engine_params = dict(json_serializer=json_serialization.dumps)

db_async_session, db_async_session_manager, async_engine = async_session_factory(
    Config.async_db_conn_str,
    **engine_params,
    echo=True,
)
