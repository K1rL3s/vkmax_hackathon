from maxhack.bot.filters.respond import RespondData
from maxhack.core.enums.respond_action import RespondStatus
from maxhack.core.max import MaxSender
from maxhack.infra.database.models import EventModel, UserModel
from maxo.types import InlineKeyboardAttachmentRequest
from maxo.types.callback_keyboard_button import CallbackKeyboardButton


class MaxNotifier:
    def __init__(self, max_sender: MaxSender) -> None:
        self._max_sender = max_sender

    async def event_notify(self, event: EventModel, user: UserModel) -> None:
        text = f"""
Событие {event.title}
        """
        keyboard = [
            [
                CallbackKeyboardButton(
                    text="✅ Буду",
                    payload=RespondData(
                        event_id=event.id,
                        status=RespondStatus.OK,
                    ).pack(),
                ),
            ],
            [
                CallbackKeyboardButton(
                    text="❓ Не уверен",
                    payload=RespondData(
                        event_id=event.id,
                        status=RespondStatus.MAYBE,
                    ).pack(),
                ),
            ],
            [
                CallbackKeyboardButton(
                    text="❌ Не смогу",
                    payload=RespondData(
                        event_id=event.id,
                        status=RespondStatus.NO,
                    ).pack(),
                ),
            ],
        ]
        attachments = InlineKeyboardAttachmentRequest.factory(keyboard)

        await self._max_sender.send_message(
            text=text,
            chat_id=user.max_chat_id,
            attachments=attachments,
        )
