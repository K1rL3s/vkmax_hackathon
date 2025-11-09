from typing import Final

from maxo.dialogs import ShowMode, StartMode
from maxo.dialogs.widgets.kbd import Start
from maxo.dialogs.widgets.text import Const

from maxhack.bot.states import Menu


def to_menu_button(
    text: str = "🏠 Меню",
    show_mode: ShowMode = ShowMode.EDIT,
) -> Start:
    return Start(
        Const(text),
        show_mode=show_mode,
        mode=StartMode.RESET_STACK,
        state=Menu.menu,
        id="to_menu",
    )


TO_MENU_BUTTON: Final = to_menu_button()
