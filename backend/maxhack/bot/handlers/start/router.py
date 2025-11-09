from maxo import Ctx, Router
from maxo.dialogs import DialogManager, ShowMode, StartMode
from maxo.routing.filters import CommandStart
from maxo.routing.updates import MessageCreated

from maxhack.bot.states import Menu

start_router = Router(name=__name__)


@start_router.message_created(CommandStart())
async def start_handler(
    message: MessageCreated,
    ctx: Ctx,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(
        state=Menu.menu,
        show_mode=ShowMode.SEND,
        mode=StartMode.RESET_STACK,
    )
