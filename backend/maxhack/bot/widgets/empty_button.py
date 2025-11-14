from typing import Any, Final

from dishka import FromDishka

from maxo.dialogs.integrations.dishka import inject
from maxo.dialogs.widgets.common import WhenCondition
from maxo.dialogs.widgets.kbd import Button
from maxo.dialogs.widgets.text import Const
from maxo.routing.updates.message_callback import MessageCallback

from maxhack.core.max import MaxSender


@inject
async def _on_empty_button(
    callback: MessageCallback,
    _: Any,
    __: Any,
    max_sender: FromDishka[MaxSender],
) -> None:
    await max_sender.callback_answer(
        query_id=callback.callback_id,
        text="🤫🧏",
    )


def empty_button(text: str = "⠀", when: WhenCondition = None) -> Button:
    return Button(
        text=Const(text),
        on_click=_on_empty_button,
        id="__empty__",
        when=when,
    )


EmptyButton: Final = empty_button()
