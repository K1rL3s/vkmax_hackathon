from collections.abc import Coroutine
from typing import Any

from maxo.bot.method_results import SendMessageResult
from maxo.errors import MaxBotBadRequestError, MaxBotForbiddenError, MaxBotNotFoundError
from maxo.fsm import State
from maxo.dialogs import BgManagerFactory, ShowMode, StartMode

from maxhack.core.ids import MaxChatId, MaxId
from maxhack.core.utils.rate_limiter import RateLimiter
from maxhack.logger import get_logger
from maxo import Bot

logger = get_logger(__name__, groups=("maxo", "max"))


class MaxSender:
    def __init__(self, bot: Bot, bg_factory: BgManagerFactory) -> None:
        self._bot = bot
        self._bg_factory = bg_factory

    @RateLimiter(max_calls=10, period=1)
    async def send_message(
        self,
        text: str,
        chat_id: int,
        **kwargs: Any,
    ) -> SendMessageResult | None:
        task = self._bot.send_message(
            chat_id=chat_id,
            text=text,
            **kwargs,
        )
        return await self._exception_logger(task)

    async def callback_answer(
        self,
        query_id: str,
        text: str | None = None,
        show_alert: bool = False,
    ) -> bool:
        task = self._bot.callback_answer(
            callback_query_id=query_id,
            text=text,
            show_alert=show_alert,
        )
        return await self._exception_logger(task)

    @RateLimiter(max_calls=10, period=1)
    async def start_dialog(
        self,
        state: State,
        user_id: MaxId,
        chat_id: MaxChatId,
        *,
        start_mode: StartMode = StartMode.RESET_STACK,
        show_mode: ShowMode = ShowMode.DELETE_AND_SEND,
        **start_kwargs: Any,
    ) -> None:
        fg_manager = self._bg_factory.bg(self._bot, user_id, chat_id)
        task = fg_manager.start(
            state=state,
            mode=start_mode,
            show_mode=show_mode,
            **start_kwargs,
        )
        return await self._exception_logger(task)

    async def _exception_logger[T](self, task: Coroutine[None, None, T]) -> T | None:
        try:
            result = await task
        except (MaxBotNotFoundError, MaxBotForbiddenError) as e:
            logger.warning(
                "Не удалось выполнить запрос, бот заблокирован или неверный chat_id",
                exc_info=e,
            )
        except MaxBotBadRequestError:
            logger.exception("Ошибка от телеграма")
        except Exception:
            logger.exception("Неизвестная ошибка")
        else:
            logger.debug(
                "Успешное выполнение таски '%s', результат: %s(%s)",
                task.__name__,
                result.__class__.__name__,
                result,
            )
            return result

        return None
