from typing import Any

from dishka import FromDishka
from magic_filter import F
from maxo import Router
from maxo.dialogs import DialogManager, ShowMode, StartMode
from maxo.dialogs.api.exceptions import (
    InvalidStackIdError,
    OutdatedIntent,
    UnknownIntent,
)
from maxo.integrations.dishka import inject
from maxo.integrations.magic_filter import MagicData
from maxo.routing.filters import AndFilter
from maxo.routing.filters.exception import ExceptionTypeFilter
from maxo.routing.signals.exception import ErrorEvent
from maxo.types.update_context import UpdateContext

from maxhack.bot.states import Errors
from maxhack.core.exceptions import MaxHackError
from maxhack.core.max import MaxSender
from maxhack.logger import get_logger

logger = get_logger(__name__, groups=("aiogd", "errors"))


errors_router = Router(name=__name__)


@errors_router.exception(
    ExceptionTypeFilter(
        UnknownIntent,
        OutdatedIntent,
        InvalidStackIdError,
    ),
)
async def on_unknown_intent(
    event: ErrorEvent[Any],
    dialog_manager: DialogManager,
    max_sender: FromDishka[MaxSender],
) -> None:
    logger.error("Перезапускаю диалог: %s", event.error, exc_info=event.error)

    if event.update.callback_query:
        callback = event.update.callback_query
        await max_sender.callback_answer(
            query_id=callback.id,
            text="😵‍💫 Кажется, возникла какая-то ошибка...",
            show_alert=False,
        )
        if callback.message:
            await callback.message.delete()

    elif event.update.message:
        message = event.update.message
        await max_sender.send_message(
            text="😵‍💫 Кажется, возникла какая то ошибка...",
            chat_id=message.chat.id,
        )

    await dialog_manager.start(
        Errors.error_intent,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@errors_router.exception(ExceptionTypeFilter(MaxHackError))
async def on_error_with_reason(
    update: ErrorEvent,
    dialog_manager: DialogManager,
) -> None:
    logger.error("Неизвестная ошибка с причиной", exc_info=update.exception)

    await dialog_manager.start(
        state=Errors.unexcepted_error,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
        data={"reason": str(update.exception)},
    )

    raise update.exception


@errors_router.error(
    AndFilter(ExceptionTypeFilter(Exception), MagicData(F.dialog_manager)),
)
async def on_unknown_error_dialogs(
    update: ErrorEvent,
    dialog_manager: DialogManager,
) -> None:
    logger.error("Неизвестная ошибка", exc_info=update.exception)

    await dialog_manager.start(
        state=Errors.unexcepted_error,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )

    raise update.exception


@errors_router.error(ExceptionTypeFilter(Exception))
@inject
async def on_unknown_error(
    update: ErrorEvent,
    update_context: UpdateContext,
    max_sender: FromDishka[MaxSender],
) -> None:
    logger.error("Неизвестная ошибка", exc_info=update.exception)

    await max_sender.send_message(
        text="😵‍💫 Неизвестная ошибка",
        chat_id=update_context.chat_id,
    )

    raise update.exception
