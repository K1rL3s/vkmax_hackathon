import asyncio

from maxo.fsm import State

from maxhack.core.max.sender import MaxSender
from maxhack.core.user.models import User


class MaxMailer:
    def __init__(self, max_sender: MaxSender) -> None:
        self._max_sender = max_sender

    async def default_message(self, text: str, users: list[User]) -> list[bool]:
        return await asyncio.gather(
            *(
                self._max_sender.send_message(text=text, chat_id=user.max_chat_id)
                for user in users
            ),
        )

    async def start_dialog(self, state: State, users: list[User]) -> None:
        await asyncio.gather(
            *(
                self._max_sender.start_dialog(
                    state=state,
                    user_id=user.max_id,
                    chat_id=user.max_chat_id,
                )
                for user in users
            ),
        )
