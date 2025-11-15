from dishka import FromDishka

from maxo.enums.message_link_type import MessageLinkType
from maxo.routing.routers.simple import Router
from maxo.routing.updates.message_callback import MessageCallback
from maxo.types.new_message_link import NewMessageLink
from maxo.utils.facades import MessageCallbackFacade

from maxhack.bot.filters.respond import RespondData
from maxhack.core.enums.respond_action import RespondStatus
from maxhack.core.exceptions import MaxHackError
from maxhack.core.ids import EventId
from maxhack.core.responds.service import RespondService
from maxhack.database.models import UserModel

respond_router = Router(__name__)


@respond_router.message_callback(RespondData.filter())
async def respond_handler(
    callback: MessageCallback,
    payload: RespondData,
    facade: MessageCallbackFacade,
    current_user: UserModel,
    respond_service: FromDishka[RespondService],
) -> None:
    event_id = EventId(int(payload.event_id))
    try:
        respond = await respond_service.get_user_respond(
            event_id,
            current_user.id,
        )
    except MaxHackError:
        respond = await respond_service.create(
            [current_user.id],
            event_id,
            payload.status,
        )
    else:
        respond = await respond_service.update(
            respond.id,
            current_user.id,
            payload.status,
        )

    if respond.status == RespondStatus.OK:
        emoji = "Буду 👍"
    elif respond.status == RespondStatus.NO:
        emoji = "Не буду 👎"
    elif respond.status == RespondStatus.MAYBE:
        emoji = "Подумаю 🤔"
    else:
        emoji = "-"

    await facade.edit_message()
    await facade.send_message(
        text=f"Отклик записан: {emoji}",
        link=NewMessageLink(
            mid=callback.unsafe_message.unsafe_body.mid,
            type=MessageLinkType.REPLY,
        ),
    )
