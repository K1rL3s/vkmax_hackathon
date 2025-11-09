from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.text import Const, Format

from maxhack.bot.handlers.getters import get_current_user
from maxhack.bot.states import Profile
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON

_profile = Window(
    Const("🐵 Твой профиль\n"),
    Format("Имя: {first_name}"),
    Format("Фамилия: {last_name}", when="last_name"),
    Format("Телефон: {phone}", when="phone"),
    TO_MENU_BUTTON,
    getter=get_current_user,
    state=Profile.my,
)

profile_dialog = Dialog(
    _profile,
)
