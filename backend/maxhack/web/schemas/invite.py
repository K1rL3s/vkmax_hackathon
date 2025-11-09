import datetime

from maxhack.core.ids import InviteKey
from maxhack.web.schemas.core import Model


class InviteCreateRequest(Model):
    expires_at: datetime.datetime


class InviteCreateResponse(Model):
    invite_key: InviteKey


class InviteAcceptRequest(Model):
    invite_key: InviteKey
