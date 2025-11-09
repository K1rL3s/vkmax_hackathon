from typing import Any

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.faststream import FastStreamProvider
from dishka.integrations.taskiq import TaskiqProvider
from maxo.integrations.dishka import MaxoProvider

from maxhack.config import Config
from maxhack.di.config import ConfigProvider
from maxhack.di.core.services import ServicesProvider
from maxhack.di.database.repos import ReposProvider
from maxhack.di.database.session import DBProvider
from maxhack.di.max_bot import MaxBotProvider


def make_container[T](
    *extra_providers: Provider,
    config: Config,
    **kwargs: Any,
) -> AsyncContainer:
    context: dict[type[T], T] = kwargs.pop("context", {})
    context[Config] = config

    return make_async_container(
        # из библиотеки
        TaskiqProvider(),
        FastapiProvider(),
        FastStreamProvider(),
        MaxoProvider(),
        # наши
        ConfigProvider(),
        DBProvider(),
        ReposProvider(),
        ServicesProvider(),
        MaxBotProvider(),
        *extra_providers,
        context=context,
        **kwargs,
    )
