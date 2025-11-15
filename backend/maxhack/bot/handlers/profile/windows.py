from magic_filter import F

from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.kbd import Button, Radio, RequestContact, RequestLocation, Url
from maxo.dialogs.widgets.text import Const, Format, HtmlSafeFormat, Multi

from . import getters, handlers
from maxhack.bot.handlers.getters import get_current_user
from maxhack.bot.states import Profile
from maxhack.bot.widgets.empty_button import empty_button
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON
from maxhack.core.enums.notify_mode import NotifyMode

_profile = Window(
    Const("Профиль 👤\n"),
    Multi(
        Const("Я знаю тебя как"),
        HtmlSafeFormat("{first_name}"),
        HtmlSafeFormat("{last_name}", when="last_name"),
        sep=" ",
    ),
    Format("📱 {phone}", when="phone"),
    Format("🌍 {formatted_timezone}"),
    RequestContact(Const("📞 Добавить телефон"), when=~F["phone"]),
    Button(
        Const("🗑️ Удалить телефон"),
        on_click=handlers.on_delete_phone,
        when="phone",
        id="delete_phone",
    ),
    RequestLocation(
        Const("📍 Определить часовой пояс"),
        quick=True,
    ),
    Url(
        Const("🌐 Выбрать часовой пояс"),
        Format("{settings_deeplink}"),
    ),
    Url(
        Const("🪪 Изменить имя-фамилию"),
        Format("{profile_deeplink}"),
    ),
    empty_button("🔔 Режим уведомлений:"),
    Radio(
        Format("🔘 {item[1]}"),
        Format("{item[1]}"),
        item_id_getter=lambda item: item[0],
        type_factory=lambda item: NotifyMode[item],
        items=(
            (NotifyMode.DEFAULT.name, "Звук"),
            (NotifyMode.SILENT.name, "Тихо"),
            (NotifyMode.DISABLE.name, "Игнор"),
        ),
        on_click=handlers.on_notify_mode,
        id="notify_mode",
    ),
    TO_MENU_BUTTON,
    getter=[get_current_user, getters.get_profile_deeplink],
    state=Profile.my,
)

profile_dialog = Dialog(
    _profile,
    on_start=handlers.on_start_set_notify_mode,
)
