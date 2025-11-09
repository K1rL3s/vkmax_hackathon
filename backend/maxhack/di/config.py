from dishka import Provider, Scope, from_context, provide

from maxhack.config import Config, DbConfig, MaxConfig, RedisConfig


class ConfigProvider(Provider):
    scope = Scope.APP

    config = from_context(Config)

    @provide
    async def tg_bot(self, config: Config) -> MaxConfig:
        return config.max

    @provide
    async def db(self, config: Config) -> DbConfig:
        return config.db

    @provide
    async def redis(self, config: Config) -> RedisConfig:
        return config.redis
