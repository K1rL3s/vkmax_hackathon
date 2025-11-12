from dishka import Provider, Scope, from_context, provide

from maxhack.config import MaxConfig
from maxhack.core.max import MaxMailer, MaxSender
from maxhack.core.max.notifier import MaxNotifier
from maxo import Bot
from maxo.dialogs import BgManagerFactory
from maxo.enums.text_fromat import TextFormat


class MaxBotProvider(Provider):
    scope = Scope.APP

    bg_factory = from_context(BgManagerFactory)

    @provide
    async def max_bot(self, max_config: MaxConfig) -> Bot:
        return Bot(token=max_config.token, text_format=TextFormat.HTML)

    max_sender = provide(MaxSender)
    max_mailer = provide(MaxMailer)
    max_notifier = provide(MaxNotifier)
