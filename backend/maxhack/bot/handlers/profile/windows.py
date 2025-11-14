from magic_filter import F

from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.kbd import Button, RequestContact, Url
from maxo.dialogs.widgets.text import Const, Format, HtmlSafeFormat, Multi

from . import getters, handlers
from maxhack.bot.handlers.getters import get_current_user
from maxhack.bot.states import Profile
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON

_profile = Window(
    Const("🪪 Профиль\n"),
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
    Url(
        Const("🌐 Изменить часовой пояс"),
        Format("{profile_deeplink}"),
        id="webapp",
    ),
    TO_MENU_BUTTON,
    getter=[get_current_user, getters.get_profile_deeplink],
    state=Profile.my,
)

profile_dialog = Dialog(
    _profile,
)
