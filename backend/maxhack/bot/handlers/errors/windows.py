from maxo.dialogs import Dialog, Window
from maxo.dialogs.widgets.text import Const, Format

from maxhack.bot.handlers.errors.getters import get_error_reason
from maxhack.bot.states import Errors

on_error_intent = Window(
    Const("😵‍💫 Произошла неизвестная ошибка..."),
    Const("Чтобы всё заработало, напиши /start"),
    state=Errors.error_intent,
)

on_unexcepted_error = Window(
    Const("😵‍💫 Произошла неизвестная ошибка..."),
    Format("Возможная причина: {reason}", when="reason"),
    Const("Чтобы всё заработало, напиши /start"),
    getter=get_error_reason,
    state=Errors.unexcepted_error,
)

errors_dialog = Dialog(on_error_intent, on_unexcepted_error)
