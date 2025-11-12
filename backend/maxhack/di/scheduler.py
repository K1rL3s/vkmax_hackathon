from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from taskiq import (
    InMemoryBroker,
    SmartRetryMiddleware,
    TaskiqScheduler,
    async_shared_broker,
)
from taskiq.abc.broker import AsyncBroker
from taskiq.abc.schedule_source import ScheduleSource
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListRedisScheduleSource

from maxhack.config import RedisConfig, SchedulerConfig
from maxhack.scheduler.base_client import BaseSchedulerClient
from maxhack.scheduler.log_middleware import ContextVarsMiddleware


class SchedulerProvider(Provider):
    scope = Scope.APP

    base_client = provide(BaseSchedulerClient)

    @provide
    def schedule_source(
        self,
        scheduler_config: SchedulerConfig,
        redis_config: RedisConfig,
    ) -> ScheduleSource:
        return ListRedisScheduleSource(
            url=redis_config.uri,
            prefix=scheduler_config.tasks_key,
        )

    @provide
    def broker(self) -> AsyncBroker:
        return InMemoryBroker().with_middlewares(
            ContextVarsMiddleware(),
            SmartRetryMiddleware(use_delay_exponent=True),
        )

    @provide
    def scheduler(
        self,
        broker: AsyncBroker,
        schedule_source: ScheduleSource,
    ) -> TaskiqScheduler:
        return TaskiqScheduler(
            broker=broker,
            sources=[schedule_source, LabelScheduleSource(async_shared_broker)],
        )

    @provide()
    def redis(
        self,
        redis_config: RedisConfig,
    ) -> Redis:
        return Redis(
            host=redis_config.host,
            port=redis_config.port,
            password=redis_config.password,
            db=redis_config.database,
            socket_connect_timeout=15,
            socket_timeout=5,
            retry_on_timeout=True,
        )
