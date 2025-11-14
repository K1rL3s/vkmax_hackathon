from typing import Any

from dishka import FromDishka

from maxo import Router
from maxo.dialogs import DialogManager, ShowMode
from maxo.routing.sentinels import SkipHandler
from maxo.routing.updates import MessageCreated
from maxo.types import ContactAttachmentPayload

from maxhack.bot.filters.request_contact import RequestContactFilter
from maxhack.core.user.service import UserService
from maxhack.database.models import UserModel

phone_router = Router(__name__)


@phone_router.message_created(RequestContactFilter())
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


def parse_vcard(vcard_str: str) -> dict[str, Any]:
    lines = vcard_str.strip().split("\r\n")
    data = {}

    for line in lines:
        if line.startswith("END:VCARD"):
            break
        if ":" in line:
            key, value = line.split(":", 1)
            if ";" in key:
                field_key, params_str = key.split(";", 1)
                params = {}
                for param in params_str.split(";"):
                    if "=" in param:
                        pkey, pval = param.split("=", 1)
                        params[pkey] = pval
                data[field_key] = {"value": value, "params": params}
            else:
                data[key] = {"value": value, "params": {}}

    return data
