import logging

from maxhack.logger.bot.context_vars import (
    current_event_type,
    current_extra_data,
    current_task_id,
    current_task_name,
    current_update,
    current_user,
    current_user_end_state,
    current_user_start_state,
)


class InjectFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # бот
        update = current_update.get()
        user = current_user.get()
        start_state = current_user_start_state.get()
        end_state = current_user_end_state.get()
        event_type = current_event_type.get()

        record.update_id = getattr(update, "update_id", None)
        record.max_id = getattr(user, "id", None)
        record.start_state = getattr(start_state, "state", None)
        record.end_state = getattr(end_state, "state", None)
        record.event_type = event_type

        # шедулер
        task_id = current_task_id.get()
        task_name = current_task_name.get()

        record.scheduler_task_id = task_id
        record.scheduler_task_name = task_name

        # остальное
        extra_data = current_extra_data.get() or {}

        record.extra_data = extra_data

        return True
