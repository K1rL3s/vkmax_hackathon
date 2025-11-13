from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.kbd import Radio, WebApp
from maxo.dialogs.widgets.text import Const, Format

from . import handlers
from maxhack.bot.handlers.getters import get_current_user
from maxhack.bot.states import Menu
from maxhack.bot.widgets.to_groups import TO_GROUPS_BUTTON
from maxhack.core.enums.notify_mode import NotifyMode

_menu = Window(
    Format("<b>👋 Привет, {first_name}!</b>\n"),
    TO_GROUPS_BUTTON,
    WebApp(
        Const("🖼️ Вебапп"),
        Format("{middleware_data[bot].state.info.username}"),
        id="webapp",
    ),
    Radio(
        Format("🔔 {item[1]}"),
        Format("{item[1]}"),
        item_id_getter=lambda item: item[0],
        type_factory=lambda item: NotifyMode[item],
        items=(
            (NotifyMode.DEFAULT.name, "Со звуком"),
            (NotifyMode.SILENT.name, "Бесшумно"),
            (NotifyMode.DISABLE.name, "Игнор"),
        ),
        on_click=handlers.on_notify_mode,
        id="notify_mode",
    ),
    getter=get_current_user,
    state=Menu.menu,
)

menu_dialog = Dialog(
    _menu,
    on_start=handlers.on_start_set_notify_mode,
)
