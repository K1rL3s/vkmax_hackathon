from magic_filter import F

from maxhack.bot.handlers.general import answer_str_error
from maxhack.bot.states import GroupsCreate
from maxhack.bot.widgets.to_groups import TO_GROUPS_BUTTON
from maxhack.bot.widgets.to_menu import TO_MENU_BUTTON
from maxo.dialogs import Dialog, ShowMode, Window
from maxo.dialogs.widgets.input import TextInput
from maxo.dialogs.widgets.kbd import Button, SwitchTo
from maxo.dialogs.widgets.text import Const, Format

from . import handlers

# TODO: Починить ввод описания

_wait_name = Window(
    Const("✏️ Введи название новой группы"),
    Const("(Его можно будет изменить)"),
    TO_GROUPS_BUTTON,
    TO_MENU_BUTTON,
    TextInput(
        type_factory=handlers.validate_group_name,
        on_error=answer_str_error,
        on_success=handlers.on_group_name,
        id="group_name",
    ),
    state=GroupsCreate.wait_name,
)

_wait_description = Window(
    Format("Название: {dialog_data[group_name]}\n"),
    Const("📋 Введи описание новой группы"),
    Const("(Его можно будет изменить)"),
    SwitchTo(
        Const("🔄 Изменить название"),
        state=GroupsCreate.wait_name,
        show_mode=ShowMode.EDIT,
        id="to_name",
    ),
    SwitchTo(
        Const("⏭️ Пропустить описание"),
        state=GroupsCreate.confirm,
        show_mode=ShowMode.EDIT,
        id="skip",
    ),
    TO_GROUPS_BUTTON,
    TO_MENU_BUTTON,
    TextInput(
        type_factory=handlers.validate_group_description,
        on_error=answer_str_error,
        on_success=handlers.on_group_description,
        id="group_description",
    ),
    state=GroupsCreate.wait_description,
)

_wait_timezone = Window(
    Format("Название: {dialog_data[group_name]}"),
    Format(
        "Описание: {dialog_data[group_description]}",
        when=F["dialog_data"]["group_description"],
    ),
    Const("\n⏰ Введи таймзону новой группы"),
    Const("(Её можно будет изменить)"),
    SwitchTo(
        Const("🔄 Изменить название"),
        state=GroupsCreate.wait_name,
        show_mode=ShowMode.EDIT,
        id="to_name",
    ),
    SwitchTo(
        Const("🔄 Изменить описание"),
        state=GroupsCreate.wait_description,
        show_mode=ShowMode.EDIT,
        id="to_description",
    ),
    SwitchTo(
        Const("⏭️ Пропустить таймозну"),
        state=GroupsCreate.confirm,
        show_mode=ShowMode.EDIT,
        id="skip",
    ),
    TO_GROUPS_BUTTON,
    TO_MENU_BUTTON,
    TextInput(
        type_factory=handlers.validate_group_timezone,
        on_error=answer_str_error,
        on_success=handlers.on_group_timezone,
        id="group_description",
    ),
    state=GroupsCreate.wait_timezone,
)

_confirm = Window(
    Format("Название: {dialog_data[group_name]}"),
    Format(
        "Описание: {dialog_data[group_description]}",
        when=F["dialog_data"]["group_description"],
    ),
    Format(
        "Таймзона: {dialog_data[group_timezone]}",
        when=F["dialog_data"]["group_timezone"],
    ),
    Const("\n❓ Создать группу?"),
    Button(Const("✅ Создать"), on_click=handlers.on_create_confirm, id="confirm"),
    SwitchTo(
        Const("🔄 Изменить название"),
        state=GroupsCreate.wait_name,
        show_mode=ShowMode.EDIT,
        id="to_name",
    ),
    SwitchTo(
        Const("🔄 Изменить описание"),
        state=GroupsCreate.wait_description,
        show_mode=ShowMode.EDIT,
        id="to_description",
    ),
    SwitchTo(
        Const("🔄 Изменить таймзону"),
        state=GroupsCreate.wait_timezone,
        show_mode=ShowMode.EDIT,
        id="to_timezone",
    ),
    TO_GROUPS_BUTTON,
    TO_MENU_BUTTON,
    state=GroupsCreate.confirm,
)

create_group_dialog = Dialog(
    _wait_name,
    _wait_description,
    _wait_timezone,
    _confirm,
)
