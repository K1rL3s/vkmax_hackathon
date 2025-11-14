from typing import Any

from dishka import FromDishka

from maxo.dialogs import DialogManager
from maxo.dialogs.integrations.dishka import inject
from maxo.dialogs.widgets.kbd import ManagedRadio

from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.user.service import UserService
from maxhack.database.models import UserModel


@inject
async def on_start_set_notify_mode(_: Any, dialog_manager: DialogManager) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    radio: ManagedRadio[str] = dialog_manager.find("notify_mode")
    await radio.set_checked(current_user.notify_mode)


@inject
async def on_notify_mode(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    notify_mode: NotifyMode,
    user_service: FromDishka[UserService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    await user_service.update_user(current_user.id, notify_mode=notify_mode)


@inject
async def on_delete_phone(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    await user_service.update_user(current_user.id, phone="")
