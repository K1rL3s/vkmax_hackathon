from typing import Any

from maxo.routing.ctx import Ctx
from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.middlewares.event_context import EVENT_FROM_USER_KEY
from maxo.routing.updates import MessageCallback, MessageCreated


class ThrottlingMiddleware(BaseMiddleware[MessageCreated | MessageCallback]):
    __slots__ = ("_cache",)

    def __init__(self) -> None:
        self._cache = set()

    async def __call__(
        self,
        update: MessageCreated | MessageCallback,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        if (user := ctx.get(EVENT_FROM_USER_KEY)) is not None:
            user_id = user.user_id
            if user_id in self._cache:
                return None
            self._cache.add(user_id)
        else:
            user_id = None

        try:
            return await next(ctx)
        finally:
            self._cache.discard(user_id)
