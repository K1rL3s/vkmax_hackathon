from typing import Any

from maxo.dialogs import DialogManager
from maxo.dialogs.integrations.dishka import inject

from maxhack.core.utils.timezones import TIMEZONES
from maxhack.database.models import UserModel


@inject
async def get_current_user(dialog_manager: DialogManager, **__: Any) -> dict[str, Any]:
    user: UserModel = dialog_manager.middleware_data["current_user"]
    # TODO: Красивая тайзмона
    return {
        "current_user": user,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "formatted_timezone": TIMEZONES.get(user.timezone, user.timezone),
    }
