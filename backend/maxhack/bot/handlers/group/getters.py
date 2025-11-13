from typing import Any

from dishka import FromDishka

from maxhack.core.exceptions import GroupNotFound, InviteNotFound, MaxHackError
from maxhack.core.group.service import GroupService
from maxhack.core.ids import GroupId
from maxhack.core.invite.service import InviteService
from maxhack.core.max import QRCoder
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.user.service import UserService
from maxhack.infra.database.models import UserModel
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.utils.utils import to_base64
from maxo import Bot
from maxo.dialogs import DialogManager
from maxo.dialogs.integrations.dishka import inject


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
                group.id,
                group.name, role.emoji,
                bot.state.info.username,
                to_base64(f'{{"path": "/groups/{group.id}"}}'),
            )
            for group, role in groups
        ],
    }


@inject
async def get_one_group(
    dialog_manager: DialogManager,
    current_user: UserModel,
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
        "invite_link": invite_link,
        "is_editor": role.id in (EDITOR_ROLE_ID, CREATOR_ROLE_ID),
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
