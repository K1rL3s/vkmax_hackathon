import asyncio
import sys

import granian
from granian.constants import Interfaces

from maxhack.core.config import Config

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    granian.Granian(
        "maxhack.web.main:app",
        address=Config.host,
        port=Config.port,
        interface=Interfaces.ASGI,
        reload=True,
        log_access=True,
    ).serve()
