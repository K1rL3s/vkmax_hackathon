from typing import Any

from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.middlewares.event_context import EVENT_FROM_USER_KEY
from maxo.types import User
from maxo.dialogs.api.internal import CONTEXT_KEY

from maxhack.logger.bot.context_vars import (
    current_event_type,
    current_update,
    current_user,
    current_user_end_state,
    current_user_start_state,
)
from maxo import Ctx


class OuterLoggerContextMiddleware(BaseMiddleware[Any]):
    async def __call__(
        self,
        update: Any,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        event_from_user: User = ctx[EVENT_FROM_USER_KEY]

        current_update.set(update)
        current_user.set(event_from_user)
        current_event_type.set(update.update.type)

        return await next(ctx)


class InnerLoggerContextMiddleware(BaseMiddleware[Any]):
    async def __call__(
        self,
        update: Any,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        start_state = getattr(ctx.get(CONTEXT_KEY), "state", None)
        current_user_start_state.set(start_state)

        try:
            return await next(ctx)
        finally:
            end_state = getattr(ctx.get(CONTEXT_KEY), "state", None)
            current_user_end_state.set(end_state)
