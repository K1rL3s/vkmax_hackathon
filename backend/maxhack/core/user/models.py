from dataclasses import dataclass

from maxhack.core.ids import MaxChatId, MaxId, UserId


@dataclass(slots=True, frozen=True, kw_only=True)
class User:
    id: UserId
    max_id: MaxId
    max_chat_id: MaxChatId
