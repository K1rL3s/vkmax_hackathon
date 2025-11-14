from typing import Any

from dishka import FromDishka

from maxo.dialogs import DialogManager
from maxo.dialogs.integrations.dishka import inject

from maxhack.core.user.service import UserService
from maxhack.database.models import UserModel


@inject
async def on_delete_phone(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    await user_service.update_user(current_user.id, phone="")
