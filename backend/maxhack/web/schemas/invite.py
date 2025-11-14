from maxhack.core.ids import InviteKey
from maxhack.web.schemas.core import Model


class InviteGetResponse(Model):
    invite_key: InviteKey
    invite_link: str


class InviteCreateResponse(Model):
    invite_key: InviteKey
    invite_link: str
