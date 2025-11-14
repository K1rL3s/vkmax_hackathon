import json
from typing import Any

from dishka import FromDishka

from maxo import Bot
from maxo.dialogs import DialogManager
from maxo.dialogs.integrations.dishka import inject
from maxo.utils.deeplink import create_startapp_link

from maxhack.core.exceptions import GroupNotFound, InviteNotFound
from maxhack.core.ids import GroupId
from maxhack.core.user.service import UserService
from maxhack.database.models import UserModel
from maxhack.database.repos.group import GroupRepo


@inject
async def get_my_groups(
    current_user: UserModel,
    user_service: FromDishka[UserService],
    bot: Bot,
    **__: Any,
) -> dict[str, Any]:
    groups = await user_service.get_user_groups(current_user.id, current_user.id)
    return {
        "groups": [
            (
                role.emoji,
                group.name,
                create_startapp_link(
                    bot,
                    json.dumps({"path": f"/groups/{group.id}"}),
                    encode=True,
                ),
            )
            for group, role in groups
        ],
    }


@inject
async def get_group_preview(
    dialog_manager: DialogManager,
    group_repo: FromDishka[GroupRepo],
    **__: Any,
) -> dict[str, Any]:
    if "invite_key" not in dialog_manager.dialog_data:
        raise InviteNotFound

    group_id: GroupId = dialog_manager.dialog_data["group_id"]
    group = await group_repo.get_by_id(group_id)
    if group is None:
        raise GroupNotFound

    return {"group": group}
