from dishka import FromDishka
from magic_filter import F

from maxo import Router
from maxo.dialogs import DialogManager, ShowMode, StartMode
from maxo.integrations.magic_filter import MagicData
from maxo.routing.filters.deeplink import DeeplinkFilter
from maxo.routing.filters.logic import AndFilter
from maxo.routing.sentinels import SkipHandler
from maxo.routing.updates.bot_started import BotStarted

from maxhack.bot.states import Groups
from maxhack.core.exceptions import MaxHackError
from maxhack.core.group.service import GroupService
from maxhack.core.ids import InviteKey
from maxhack.core.invite.service import InviteService
from maxhack.core.max import MaxSender
from maxhack.core.max.deeplinker import InvitePrefix
from maxhack.database.models import UserModel

deeplinks_router = Router(name=__name__)


@deeplinks_router.bot_started(
    AndFilter(
        DeeplinkFilter(),
        MagicData(F.deeplink.startswith(InvitePrefix)),
    ),
)
async def invite_deeplink_handler(
    event: BotStarted,
    deeplink: str,
    dialog_manager: DialogManager,
    current_user: UserModel,
    invite_service: FromDishka[InviteService],
    group_service: FromDishka[GroupService],
    max_sender: FromDishka[MaxSender],
) -> None:
    raw_invite_key = deeplink[len(InvitePrefix) :]
    try:
        invite_key = InviteKey(str(raw_invite_key))
    except ValueError as e:
        raise SkipHandler from e

    dialog_manager.show_mode = ShowMode.SEND

    try:
        invite, group = await invite_service.is_valid_key(invite_key)
    except MaxHackError as e:
        await max_sender.send_message(
            text="😵‍💫 Не нашёл такое приглашение...",
            chat_id=event.chat_id,
        )
        raise SkipHandler from e

    try:
        await group_service.get_group(current_user.id, group.id)
    except MaxHackError:
        await dialog_manager.start(
            state=Groups.join,
            show_mode=ShowMode.SEND,
            mode=StartMode.RESET_STACK,
            data={"invite_key": invite.key, "group_id": group.id},
        )
    else:
        await dialog_manager.start(
            state=Groups.one,
            show_mode=ShowMode.SEND,
            mode=StartMode.RESET_STACK,
            data={"group_id": group.id},
        )
