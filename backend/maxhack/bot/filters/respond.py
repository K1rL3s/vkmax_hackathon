from dataclasses import dataclass

from maxhack.core.enums.respond_action import RespondStatus
from maxhack.core.ids import EventId
from maxo.routing.filters.payload import Payload


@dataclass
class RespondData(Payload, prefix="respond"):
    event_id: EventId
    status: RespondStatus
