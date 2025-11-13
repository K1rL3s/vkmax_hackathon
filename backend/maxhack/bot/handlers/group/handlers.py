from typing import Any

from dishka import FromDishka

from maxhack.bot.states import Menu
from maxhack.core.exceptions import MaxHackError
from maxhack.core.group.service import GroupService
from maxhack.core.ids import InviteKey
from maxhack.infra.database.models import UserModel
from maxo.dialogs import DialogManager, ShowMode
from maxo.dialogs.integrations.dishka import inject


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
    except MaxHackError as e:
        # TODO: Сообщение что инвайт истёк
        raise e

    # TODO: Сообщение с стартапп в группу
    await dialog_manager.switch_to(state=Menu.menu, show_mode=ShowMode.EDIT)
