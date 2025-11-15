from magic_filter import F

from maxo.dialogs import Dialog, ShowMode, Window
from maxo.dialogs.widgets.kbd import Button, Column, Radio, Select, SwitchTo, Url
from maxo.dialogs.widgets.text import Const, Format

from . import getters, handlers
from maxhack.bot.handlers.utils import on_start_update_dialog_data
from maxhack.bot.states import Groups
from maxhack.bot.widgets.empty_button import empty_button
from maxhack.bot.widgets.scrolling_group import CustomScrollingGroup
from maxhack.bot.widgets.to_groups import TO_GROUPS_BUTTON
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON, to_menu_button
from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.group.consts import PRIVATE_GROUP_NAME
from maxhack.core.ids import GroupId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID

_groups = Window(
    Const("Твои группы 👫"),
    CustomScrollingGroup(
        Select(
            text=Format("{item[1].emoji} {item[0].name}"),
            item_id_getter=lambda item: item[0].id,
            type_factory=lambda id_: GroupId(int(id_)),
            on_click=handlers.on_select_group,
            items="groups",
            id="select_group",
        ),
    ),
    Button(
        Const("📆 Выгрузить все события"),
        on_click=handlers.on_get_all_my_events,
        id="all_events",
    ),
    TO_MENU_BUTTON,
    getter=getters.get_my_groups,
    state=Groups.all,
)

_one_group = Window(
    Format("Группа {group.name} 👫"),
    Format("\nПриглашение: {invite_link}", when="invite_link"),
    Url(Const("⬆️ В группу"), Format("{group_url}")),
    Column(
        Button(
            Const("Пересоздать приглашение 🎫"),
            on_click=handlers.on_recreate_invite,
            id="recreate_invite",
        ),
        Button(
            Const("Удалить приглашение 🚮"),
            on_click=handlers.on_delete_invite,
            when="invite_link",
            id="delete_invite",
        ),
        when=F["is_editor"] & ~F["is_private"],
    ),
    Button(
        Const("📆 Выгрузить события группы"),
        on_click=handlers.on_get_all_group_events,
        when=F["role"].id.in_((CREATOR_ROLE_ID, EDITOR_ROLE_ID)),
        id="all_events",
    ),
    Button(
        Const("📆 Выгрузить мои события"),
        on_click=handlers.on_get_my_group_events,
        when=F["group"].name != PRIVATE_GROUP_NAME,
        id="my_events",
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
        on_click=handlers.on_group_notify_mode,
        id="notify_mode",
    ),
    SwitchTo(
        Const("Твои группы ⏮️"),
        state=Groups.all,
        show_mode=ShowMode.EDIT,
        id="back",
    ),
    TO_MENU_BUTTON,
    getter=getters.get_one_group,
    state=Groups.one,
)

_join_group = Window(
    Format("👫 Тебя приглашают в группу {group.name}"),
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
    _one_group,
    _join_group,
    on_start=on_start_update_dialog_data,
)
