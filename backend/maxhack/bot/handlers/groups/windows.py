from maxhack.bot.states import Groups
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON
from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.text import Const

_groups = Window(
    Const("💤 Твои группы"),
    TO_MENU_BUTTON,
    state=Groups.all,
)

groups_dialog = Dialog(
    _groups,
)
