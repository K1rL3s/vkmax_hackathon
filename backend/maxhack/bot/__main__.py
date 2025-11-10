import asyncio
import contextlib
import sys

from maxhack.bot.init_bot import init_bot
from maxhack.logger import get_logger
from maxo import Bot
from maxo.tools.long_polling import LongPolling

logger = get_logger(__name__, groups=("main", "bot", "maxbot"))


async def main() -> None:
    dp, container = await init_bot()

    bot = await container.get(Bot)
    try:
        await LongPolling(dp).start(bot)
    except Exception:
        logger.exception("Ошибка при поллинге, конец работы")
    finally:
        await container.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        # раб винды :(
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if __debug__:
        runner = asyncio.run
    else:
        try:
            import uvloop

            runner = uvloop.run
        except ImportError:
            runner = asyncio.run

    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        runner(main())
