from dishka import Provider, Scope, from_context, provide
from maxo.dialogs import BgManagerFactory

from maxhack.config import MaxConfig
from maxhack.core.max import MaxMailer, MaxSender
from maxo import Bot


class MaxBotProvider(Provider):
    scope = Scope.APP

    bg_factory = from_context(BgManagerFactory)

    @provide
    async def max_bot(self, max_config: MaxConfig) -> Bot:
        return Bot(token=max_config.token)

    max_sender = provide(MaxSender)
    max_mailer = provide(MaxMailer)
