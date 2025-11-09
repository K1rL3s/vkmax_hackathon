from contextvars import ContextVar
from typing import Any

from maxo.fsm import State
from maxo.routing.updates import BaseUpdate
from maxo.types import User

current_update: ContextVar[BaseUpdate | None] = ContextVar("max_update", default=None)
current_user: ContextVar[User | None] = ContextVar("max_user", default=None)
current_user_start_state: ContextVar[State | None] = ContextVar(
    "user_start_state",
    default=None,
)
current_user_end_state: ContextVar[State | None] = ContextVar(
    "user_end_state",
    default=None,
)
current_event_type: ContextVar[str | None] = ContextVar(
    "event_type",
    default=None,
)

current_task_id: ContextVar[str | None] = ContextVar("task_id", default=None)
current_task_name: ContextVar[str | None] = ContextVar("task_name", default=None)
current_extra_data: ContextVar[dict[str, Any] | None] = ContextVar(
    "extra_data",
    default=None,
)
