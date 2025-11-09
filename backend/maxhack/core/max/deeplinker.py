from typing import Any

from maxhack.core.ids import InviteKey

InvitePrefix = "invite_"


class Deeplinker:
    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name

    def invite_deeplink(self, invite_key: InviteKey) -> str:
        return self._generate_deeplink(InvitePrefix, invite_key)

    def _generate_deeplink(self, prefix: str, data: Any) -> str:
        return f"https://max.ru/{self.bot_name}?start={prefix}{data}"
