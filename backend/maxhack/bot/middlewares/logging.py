import asyncio
from typing import Any

from maxo import Ctx
from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.sentinels import REJECTED, UNHANDLED
from maxo.routing.signals import Update

from maxhack.logger import get_logger

logger = get_logger(__name__, groups=("maxo", "max", "middlewares"))


class LoggingMiddleware(BaseMiddleware[Update]):
    async def __call__(
        self,
        update: Update,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        is_handled = False
        update_id = update.marker
        bot_id = ctx["bot"].state.info.user_id

        logger.debug("Start process update id=%s by bot id=%s", update_id, bot_id)
        try:
            response = await next(ctx)
            is_handled = response not in (UNHANDLED, REJECTED)
            return response
        except Exception:
            logger.debug(
                "Cause exception while process update id=%s by bot id=%s",
                update_id,
                bot_id,
            )
            raise
        finally:
            finish_time = loop.time()
            duration = (finish_time - start_time) * 1000
            logger.debug(
                "Update id=%s is %s. Duration %d ms by bot id=%d",
                update_id,
                "handled" if is_handled else "not handled",
                duration,
                bot_id,
            )
