from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.text import Const

from maxhack.bot.states import Groups
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON

_groups = Window(
    Const("💤 Твои группы"),
    TO_MENU_BUTTON,
    state=Groups.all,
)

groups_dialog = Dialog(
    _groups,
)
