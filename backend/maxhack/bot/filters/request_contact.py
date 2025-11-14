from maxo import Ctx
from maxo.routing.filters import BaseFilter
from maxo.routing.updates import MessageCreated
from maxo.types import ContactAttachment


class RequestContactFilter(BaseFilter[MessageCreated]):
    async def __call__(self, update: MessageCreated, ctx: Ctx) -> bool:
        if update.message.body is None:
            return False
        if not update.message.body.attachments:
            return False
        for attachment in update.message.body.attachments:
            if isinstance(attachment, ContactAttachment):
                ctx["contact_payload"] = attachment.payload
                return True
        return False
