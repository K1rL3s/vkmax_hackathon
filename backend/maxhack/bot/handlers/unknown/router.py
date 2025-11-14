from typing import Any

from dishka import FromDishka

from maxo import Router
from maxo.dialogs import DialogManager, ShowMode, StartMode
from maxo.types.update_context import UpdateContext

from maxhack.bot.states import Menu
from maxhack.core.max import MaxSender

unknown_router = Router(__name__)


@unknown_router.message_created()
@unknown_router.message_callback()
async def unknown_message(
    _: Any,
    update_context: UpdateContext,
    dialog_manager: DialogManager,
    max_sender: FromDishka[MaxSender],
) -> None:
    await max_sender.send_message(text="🤔", chat_id=update_context.chat_id)
    await dialog_manager.start(
        state=Menu.menu,
        show_mode=ShowMode.SEND,
        mode=StartMode.RESET_STACK,
    )
