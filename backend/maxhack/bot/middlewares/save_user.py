from typing import Any, cast

from dishka import AsyncContainer

from maxo.integrations.dishka import CONTAINER_NAME
from maxo.routing.ctx import Ctx
from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.middlewares.event_context import EVENT_FROM_USER_KEY
from maxo.routing.middlewares.update_context import UPDATE_CONTEXT_KEY
from maxo.types import User as MaxUser
from maxo.types.update_context import UpdateContext

from maxhack.core.ids import MaxChatId, MaxId
from maxhack.core.user.service import UserService
from maxhack.database.models import UserModel
from maxhack.logger import get_logger

logger = get_logger(__name__, groups=("maxo", "max", "middlewares"))


class SaveUserMiddleware(BaseMiddleware[Any]):
    async def __call__(
        self,
        update: Any,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        if (max_user := cast(MaxUser, ctx.get(EVENT_FROM_USER_KEY))) is None:
            return await next(ctx)

        db_user: UserModel | None = ctx["current_user"]

        if db_user is None:
            update_context: UpdateContext = ctx[UPDATE_CONTEXT_KEY]
            container: AsyncContainer = ctx[CONTAINER_NAME]
            user_service = await container.get(UserService)
            max_id = MaxId(max_user.id)
            db_user = await user_service.create_user(
                max_id=max_id,
                max_chat_id=MaxChatId(update_context.chat_id),
                first_name=max_user.first_name,
                last_name=max_user.last_name,
            )
            logger.info("Новый пользователь: %s", db_user)

        ctx["current_user"] = db_user
        return await next(ctx)
