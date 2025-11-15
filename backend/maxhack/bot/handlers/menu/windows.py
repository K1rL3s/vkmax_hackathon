from maxo.dialogs import Dialog, ShowMode, StartMode, Window
from maxo.dialogs.widgets.kbd import Start, WebApp
from maxo.dialogs.widgets.text import Const, Format, HtmlSafeFormat

from maxhack.bot.handlers.getters import get_current_user
from maxhack.bot.states import Menu, Profile
from maxhack.bot.widgets.to_groups import TO_GROUPS_BUTTON

_menu = Window(
    HtmlSafeFormat("<b>{greeting}, {first_name} {greeting_emoji}</b>\n"),
    TO_GROUPS_BUTTON,
    Start(
        Const("👤 Профиль"),
        state=Profile.my,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        id="to_profile",
    ),
    WebApp(
        Const("🖼️ Вебапп"),
        Format("{middleware_data[bot].state.info.username}"),
    ),
    getter=get_current_user,
    state=Menu.menu,
)

menu_dialog = Dialog(
    _menu,
)
