from maxhack.bot.handlers.getters import get_current_user
from maxhack.bot.states import Menu
from maxhack.bot.widgets.to_groups import TO_GROUPS_BUTTON
from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.kbd import WebApp
from maxo.dialogs.widgets.text import Const, Format

_menu = Window(
    Format("<b>👋 Привет, {first_name}!</b>"),
    TO_GROUPS_BUTTON,
    WebApp(
        Const("🖼️ Вебапп"),
        Format("{middleware_data[bot].state.info.username}"),
        id="webapp",
    ),
    getter=get_current_user,
    state=Menu.menu,
)

menu_dialog = Dialog(
    _menu,
)
