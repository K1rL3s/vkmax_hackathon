from typing import Any

from maxo.routing.ctx import Ctx
from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.middlewares.event_context import EVENT_FROM_USER_KEY
from maxo.routing.signals import Update
from maxo.dialogs.api.entities import EVENT_CONTEXT_KEY, DialogUpdate
from maxo.dialogs.context.intent_middleware import event_context_from_aiogd


class AiogdUserContextMiddleware(BaseMiddleware[Update]):
    async def __call__(
        self,
        update: Update,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        if isinstance(update, DialogUpdate):
            event_context = event_context_from_aiogd(update.aiogd_update)
            ctx[EVENT_CONTEXT_KEY] = event_context
            if event_context.user is not None:
                ctx[EVENT_FROM_USER_KEY] = event_context.user

        return await next(ctx)
