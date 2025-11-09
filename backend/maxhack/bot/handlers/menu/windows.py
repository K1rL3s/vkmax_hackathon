from maxo.dialogs import Dialog, ShowMode, StartMode, Window
from maxo.dialogs.widgets.kbd import Start
from maxo.dialogs.widgets.text import Const, Format

from maxhack.bot.handlers.getters import get_current_user
from maxhack.bot.states import Groups, Menu, Profile

_menu = Window(
    Format("👋 Привет, {first_name}!"),
    Start(
        Const("💤 Группы"),
        state=Groups.all,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        id="to_groups",
    ),
    Start(
        Const("🐵 Профиль"),
        state=Profile.my,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        id="to_profile",
    ),
    getter=get_current_user,
    state=Menu.menu,
)

menu_dialog = Dialog(
    _menu,
)
