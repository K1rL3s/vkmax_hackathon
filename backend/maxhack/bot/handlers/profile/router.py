from dishka import FromDishka

from maxo import Router
from maxo.dialogs import DialogManager, ShowMode
from maxo.routing.sentinels import SkipHandler
from maxo.routing.updates import MessageCreated
from maxo.types import ContactAttachmentPayload, LocationAttachment

from .utils import parse_vcard, tz_name_from_latlon, utc_offset_minutes
from maxhack.bot.filters.location_filter import LocationFilter
from maxhack.bot.filters.request_contact import RequestContactFilter
from maxhack.core.user.service import UserService
from maxhack.database.models import UserModel

profile_router = Router(__name__)


@profile_router.message_created(RequestContactFilter())
async def request_contact_handler(
    _: MessageCreated,
    contact_payload: ContactAttachmentPayload,
    dialog_manager: DialogManager,
    current_user: UserModel,
    user_service: FromDishka[UserService],
) -> None:
    if (
        contact_payload.max_info
        and contact_payload.max_info.user_id != current_user.max_id
    ):
        raise SkipHandler
    if not contact_payload.vcf_info:
        # TODO: Сообщение что нет данных
        raise SkipHandler

    vcf = parse_vcard(contact_payload.vcf_info)

    phone_number = vcf.get("TEL", {}).get("value", None)
    if phone_number:
        phone_number = "+" + phone_number

    await user_service.update_user(current_user.id, phone=phone_number)

    await dialog_manager.show(show_mode=ShowMode.SEND)


@profile_router.message_created(LocationFilter())
async def request_contact_handler(
    _: MessageCreated,
    location_attachment: LocationAttachment,
    dialog_manager: DialogManager,
    current_user: UserModel,
    user_service: FromDishka[UserService],
) -> None:
    timezone = utc_offset_minutes(
        tz_name_from_latlon(
            location_attachment.latitude,
            location_attachment.longitude,
        ),
    )

    await user_service.update_user(current_user.id, timezone=timezone)

    await dialog_manager.show(show_mode=ShowMode.SEND)
