from datetime import timedelta

from magic_filter import F

from maxhack.bot.handlers import (
    commands_router,
    create_group_dialog,
    errors_dialog,
    errors_router,
    groups_dialog,
    menu_dialog,
    profile_dialog,
    respond_router,
    start_router,
)
from maxhack.bot.middlewares import (
    AiogdUserContextMiddleware,
    CurrentUserMiddleware,
    InnerLoggerContextMiddleware,
    LoggingMiddleware,
    OuterLoggerContextMiddleware,
    SaveUserMiddleware,
    ThrottlingMiddleware,
)
from maxhack.config import RedisConfig
from maxo import Dispatcher
from maxo.dialogs import BgManagerFactory, setup_dialogs
from maxo.enums import ChatType
from maxo.fsm.key_builder import DefaultKeyBuilder
from maxo.fsm.storages.memory import DisabledEventIsolation
from maxo.fsm.storages.redis import RedisStorage
from maxo.integrations.magic_filter import MagicFilter


async def init_dispatcher(
    redis_config: RedisConfig,
) -> tuple[Dispatcher, BgManagerFactory]:
    key_builder = DefaultKeyBuilder(with_destiny=True)

    storage = RedisStorage.from_url(
        redis_config.uri,
        key_builder=key_builder,
        state_ttl=timedelta(days=30),
        data_ttl=timedelta(days=30),
        connection_kwargs={
            "socket_connect_timeout": 15,
            "socket_timeout": 5,
            "retry_on_timeout": True,
        },
    )

    dp = Dispatcher(
        storage=storage,
        events_isolation=DisabledEventIsolation(),
        key_builder=key_builder,
    )

    dp.update.middleware.outer(LoggingMiddleware())
    dp.update.middleware.inner(CurrentUserMiddleware())
    dp.message_created.middleware.inner(SaveUserMiddleware())
    dp.bot_started.middleware.inner(SaveUserMiddleware())
    dp.message_created.middleware.outer(ThrottlingMiddleware())
    dp.message_callback.middleware.outer(ThrottlingMiddleware())

    dp.message_created.filter(MagicFilter(F.chat.type == ChatType.DIALOG))
    dp.include(
        errors_router,
        commands_router,
        start_router,
        respond_router,
        errors_dialog,
        menu_dialog,
        profile_dialog,
        groups_dialog,
        create_group_dialog,
    )

    bg_factory = setup_dialogs(dp, events_isolation=DisabledEventIsolation())

    dp.update.middleware.outer(AiogdUserContextMiddleware())
    dp.update.middleware.outer(OuterLoggerContextMiddleware())
    dp.message_created.middleware.inner(InnerLoggerContextMiddleware())
    dp.message_callback.middleware.inner(InnerLoggerContextMiddleware())

    return dp, bg_factory
