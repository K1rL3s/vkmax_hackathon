import asyncio

from maxhack.core.max.notifier import MaxNotifier
from maxhack.core.max.sender import MaxSender
from maxhack.infra.database.models import EventModel, UserModel
from maxo.fsm import State


class MaxMailer:
    def __init__(self, max_sender: MaxSender, max_notifier: MaxNotifier) -> None:
        self._max_sender = max_sender
        self._max_notifier = max_notifier

    async def default_message(self, text: str, users: list[UserModel]) -> None:
        await asyncio.gather(
            *(
                self._max_sender.send_message(text=text, chat_id=user.max_chat_id)
                for user in users
            ),
        )

    async def start_dialog(self, state: State, users: list[UserModel]) -> None:
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

    async def notify_event(self, event: EventModel, users: list[UserModel]) -> None:
        await asyncio.gather(
            *(self._max_notifier.event_notify(event, user) for user in users),
        )
