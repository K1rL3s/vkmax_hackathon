import json
from typing import Any

from dishka import FromDishka

from maxo import Bot
from maxo.dialogs import DialogManager
from maxo.dialogs.integrations.dishka import inject
from maxo.utils.deeplink import create_startapp_link

from maxhack.core.exceptions import GroupNotFound, InviteNotFound, MaxHackError
from maxhack.core.group.consts import PRIVATE_GROUP_NAME
from maxhack.core.group.service import GroupService
from maxhack.core.ids import GroupId
from maxhack.core.invite.service import InviteService
from maxhack.core.max import QRCoder
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.user.service import UserService
from maxhack.database.models import UserModel
from maxhack.database.repos.group import GroupRepo


@inject
async def get_my_groups(
    current_user: UserModel,
    user_service: FromDishka[UserService],
    **__: Any,
) -> dict[str, Any]:
    groups = await user_service.get_user_groups(current_user.id, current_user.id)
    return {"groups": groups}


@inject
async def get_one_group(
    dialog_manager: DialogManager,
    current_user: UserModel,
    bot: Bot,
    group_service: FromDishka[GroupService],
    invite_service: FromDishka[InviteService],
    qrcoder: FromDishka[QRCoder],
    **__: Any,
) -> dict[str, Any]:
    group_id: GroupId = dialog_manager.dialog_data["group_id"]
    group, role = await group_service.get_group(current_user.id, group_id)
    try:
        invite = await invite_service.get_invite(group_id, current_user.id)
        invite_link = qrcoder.invite_deeplink(invite.key) if invite else None
    except MaxHackError:
        invite_link = None

    return {
        "group": group,
        "role": role,
        "group_url": create_startapp_link(
            bot,
            json.dumps({"path": f"/groups/{group.id}"}),
            encode=True,
        ),
        "invite_link": invite_link,
        "is_editor": role.id in (CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        "is_private": group.name == PRIVATE_GROUP_NAME,
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
