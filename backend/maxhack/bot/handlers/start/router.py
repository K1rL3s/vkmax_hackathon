from typing import Any

from maxhack.bot.states import Menu
from maxo import Router
from maxo.dialogs import DialogManager, ShowMode, StartMode
from maxo.routing.filters import CommandStart

start_router = Router(name=__name__)


@start_router.message_created(CommandStart())
@start_router.bot_started()
async def start_handler(
    _: Any,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(
        state=Menu.menu,
        show_mode=ShowMode.SEND,
        mode=StartMode.RESET_STACK,
    )
