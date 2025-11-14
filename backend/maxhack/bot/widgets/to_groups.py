from typing import Final

from maxo.dialogs import ShowMode, StartMode
from maxo.dialogs.widgets.kbd import Start
from maxo.dialogs.widgets.text import Const

from maxhack.bot.states import Groups


def to_groups_button(
    text: str = "👫 Группы",
    show_mode: ShowMode = ShowMode.EDIT,
) -> Start:
    return Start(
        Const(text),
        show_mode=show_mode,
        mode=StartMode.RESET_STACK,
        state=Groups.all,
        id="to_groups",
    )


TO_GROUPS_BUTTON: Final = to_groups_button()
