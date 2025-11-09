from dishka import AsyncContainer, Provider
from maxo.integrations.dishka import setup_dishka
from maxo.dialogs import BgManagerFactory

from maxhack.bot.dp import init_dispatcher
from maxhack.config import Config, load_config
from maxhack.di import make_container
from maxhack.logger import setup_logger
from maxo import Dispatcher


async def init_bot(
    env_path: str | None = None,
) -> tuple[Dispatcher, AsyncContainer]:
    config = load_config(env_path)

    setup_logger(config.log_level)

    dp, bg_factory = await init_dispatcher(config.redis)
    container = await init_container(dp, bg_factory, config)

    return dp, container


async def init_container(
    dp: Dispatcher,
    bg_factory: BgManagerFactory,
    config: Config,
    *extra_providers: Provider,
) -> AsyncContainer:
    container = make_container(
        *extra_providers,
        config=config,
        context={Dispatcher: dp, BgManagerFactory: bg_factory},
    )
    setup_dishka(container, dp, auto_inject=True)
    return container
