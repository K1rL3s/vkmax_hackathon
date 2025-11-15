import time
from typing import Any

from dishka import FromDishka

from maxo.dialogs import DialogManager, ShowMode, StartMode
from maxo.dialogs.integrations.dishka import inject
from maxo.dialogs.widgets.kbd import ManagedRadio
from maxo.enums import UploadType
from maxo.utils.facades import MessageCreatedFacade
from maxo.utils.upload_media import BufferedInputFile

from maxhack.bot.states import Groups, Menu
from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.exceptions import MaxHackError
from maxhack.core.group.service import GroupService
from maxhack.core.ics.service import IcsService
from maxhack.core.ids import GroupId, InviteKey
from maxhack.database.models import UserModel


@inject
async def on_select_group(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    group_id: GroupId,
    group_service: FromDishka[GroupService],
) -> None:
    dialog_manager.dialog_data["group_id"] = group_id
    current_user: UserModel = dialog_manager.middleware_data["current_user"]

    member = await group_service.get_member(current_user.id, group_id, current_user.id)

    radio: ManagedRadio[str] = dialog_manager.find("notify_mode")
    await radio.set_checked(member.notify_mode)

    await dialog_manager.switch_to(state=Groups.one, show_mode=ShowMode.EDIT)


@inject
async def on_join_group(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    group_service: FromDishka[GroupService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    invite_key: InviteKey = dialog_manager.dialog_data["invite_key"]

    try:
        await group_service.join_group(current_user.id, invite_key)
    except MaxHackError:
        await dialog_manager.start(
            state=Menu.menu,
            show_mode=ShowMode.DELETE_AND_SEND,
            mode=StartMode.RESET_STACK,
        )
    else:
        await dialog_manager.switch_to(state=Groups.one, show_mode=ShowMode.EDIT)


@inject
async def on_get_all_my_events(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    ics_service: FromDishka[IcsService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    facade: MessageCreatedFacade = dialog_manager.middleware_data["facade"]

    raw_ics = await ics_service.export_user_events_all_groups(current_user.id)
    filename = f"user{current_user.id}_events_{int(time.time())}.ics"
    await facade.send_media(
        text="Все твои события во всех группах 📆",
        media=BufferedInputFile(raw_ics, filename, UploadType.FILE),
    )

    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


@inject
async def on_get_all_group_events(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    ics_service: FromDishka[IcsService],
    group_service: FromDishka[GroupService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    facade: MessageCreatedFacade = dialog_manager.middleware_data["facade"]
    group_id: GroupId = dialog_manager.dialog_data["group_id"]

    raw_ics = await ics_service.export_all_group_events(group_id, current_user.id)
    group, _ = await group_service.get_group(current_user.id, group_id)
    filename = f"group{group_id}_events_{int(time.time())}.ics"
    await facade.send_media(
        text=f"📆 Все события в группе {group.name}",
        media=BufferedInputFile(raw_ics, filename, UploadType.FILE),
    )

    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


@inject
async def on_get_my_group_events(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    ics_service: FromDishka[IcsService],
    group_service: FromDishka[GroupService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    facade: MessageCreatedFacade = dialog_manager.middleware_data["facade"]
    group_id: GroupId = dialog_manager.dialog_data["group_id"]

    raw_ics = await ics_service.export_user_events_in_group(group_id, current_user.id)
    if raw_ics:
        timestamp = int(time.time())
        group, _ = await group_service.get_group(current_user.id, group_id)
        filename = f"user{current_user.id}_group{group_id}_events_{timestamp}.ics"
        await facade.send_media(
            text=f"Все твои события в группе {group.name} 📆",
            media=BufferedInputFile(raw_ics, filename, UploadType.FILE),
        )

    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


@inject
async def on_group_notify_mode(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    notify_mode: NotifyMode,
    group_service: FromDishka[GroupService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    group_id: GroupId = dialog_manager.dialog_data["group_id"]
    await group_service.update_membership(
        group_id,
        current_user.id,
        current_user.id,
        notify_mode=notify_mode,
    )
