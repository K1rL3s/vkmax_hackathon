from maxhack.bot.states import Groups
from maxhack.bot.widgets.scrolling_group import CustomScrollingGroup
from maxhack.bot.widgets.to_groups import TO_GROUPS_BUTTON
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON, to_menu_button
from maxhack.bot.widgets.url_select import UrlSelect
from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.kbd import Button
from maxo.dialogs.widgets.text import Const, Format

from maxhack.bot.handlers.utils import on_start_update_dialog_data
from . import getters, handlers

_groups = Window(
    Const("💤 Твои группы"),
    CustomScrollingGroup(
        UrlSelect(
            text=Format("{item[2]} {item[1]}"),
            url=Format("https://max.ru/{item[3]}?startapp&start_param={item[4]}"),
            items="groups",
            id="select_group",
        ),
    ),
    TO_MENU_BUTTON,
    getter=getters.get_my_groups,
    state=Groups.all,
)

_join_group = Window(
    Format("💤 Тебя приглашают в группу {group.name}"),
    Button(
        Const("✅ Принять приглашение"),
        id="join",
        on_click=handlers.on_join_group,
    ),
    to_menu_button("❌ Отказаться"),
    TO_GROUPS_BUTTON,
    TO_MENU_BUTTON,
    getter=getters.get_group_preview,
    state=Groups.join,
)


groups_dialog = Dialog(
    _groups,
    _join_group,
    on_start=on_start_update_dialog_data,
)
