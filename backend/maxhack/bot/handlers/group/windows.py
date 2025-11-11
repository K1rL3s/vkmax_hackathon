from magic_filter import F

from maxhack.bot.states import Groups, GroupsCreate
from maxhack.bot.widgets.scrolling_group import CustomScrollingGroup
from maxhack.bot.widgets.to_groups import TO_GROUPS_BUTTON
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON
from maxhack.core.ids import GroupId
from maxo.dialogs import Dialog, ShowMode, StartMode, Window
from maxo.dialogs.widgets.kbd import Select, Start
from maxo.dialogs.widgets.text import Const, Format

from ..utils import on_start_update_dialog_data
from . import getters, handlers

_groups = Window(
    Const("💤 Твои группы"),
    CustomScrollingGroup(
        Select(
            Format("{item[1].emoji} {item[0].name}"),
            item_id_getter=lambda item: item[0].id,
            items="groups",
            type_factory=lambda id_: GroupId(int(id_)),
            on_click=handlers.on_select_group,
            id="select_group",
        ),
    ),
    Start(
        Const("🆕 Создать группу"),
        state=GroupsCreate.wait_name,
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK,
        id="create_group",
    ),
    TO_MENU_BUTTON,
    getter=getters.get_my_groups,
    state=Groups.all,
)

_one_group = Window(
    Format("💤 Группа {group.name}"),
    Format("{group.description}\n", when=F["group"].description),
    Format("Ты - {role.name} {role.emoji}"),
    TO_GROUPS_BUTTON,
    TO_MENU_BUTTON,
    getter=getters.get_one_group,
    state=Groups.one,
)


groups_dialog = Dialog(
    _groups,
    _one_group,
    on_start=on_start_update_dialog_data,
)
