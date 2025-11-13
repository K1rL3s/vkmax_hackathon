from maxo import Bot
from maxo.utils.long_polling import LongPolling

from maxhack.bot.init_bot import init_bot
from maxhack.logger import get_logger
from maxhack.utils.run import run

logger = get_logger(__name__, groups=("main", "bot", "maxbot"))


async def main() -> None:
    dp, container = await init_bot()

    bot = await container.get(Bot)
    try:
        await LongPolling(dp).start(bot, drop_pending_updates=True)
    except Exception:
        logger.exception("Ошибка при поллинге, конец работы")
    finally:
        await container.close()


if __name__ == "__main__":
    run(main())
