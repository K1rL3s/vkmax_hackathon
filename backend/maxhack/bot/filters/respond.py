from dataclasses import dataclass

from maxhack.core.enums.respond_action import RespondStatus
from maxo.routing.filters.payload import Payload


@dataclass
class RespondData(Payload, prefix="respond"):
    event_id: int
    status: RespondStatus
