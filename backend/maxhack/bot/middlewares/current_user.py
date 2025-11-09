from typing import Any, cast

from dishka import AsyncContainer
from dishka.integrations.taskiq import CONTAINER_NAME
from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.middlewares.event_context import EVENT_FROM_USER_KEY
from maxo.routing.signals import Update
from maxo.routing.updates.base import MaxUpdate
from maxo.types import User as MaxUser

from maxhack.core.ids import MaxId
from maxhack.infra.database.repos.user import UserRepo
from maxhack.logger import get_logger
from maxo import Ctx

logger = get_logger(__name__, groups=("maxo", "max", "middlewares"))


class CurrentUserMiddleware(BaseMiddleware[Update]):
    async def __call__(
        self,
        update: MaxUpdate,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        if (max_user := cast(MaxUser, ctx.get(EVENT_FROM_USER_KEY))) is None:
            return await next(ctx)

        if "current_user" not in ctx:
            max_id = MaxId(max_user.id)
            container: AsyncContainer = ctx[CONTAINER_NAME]
            user_repo = await container.get(UserRepo)
            db_user = await user_repo.get_by_max_id(max_id)
            ctx["current_user"] = db_user

        return await next(ctx)
