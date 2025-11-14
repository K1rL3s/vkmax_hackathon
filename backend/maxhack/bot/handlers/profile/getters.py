import json
from typing import Any

from maxo import Bot
from maxo.utils.deeplink import create_startapp_link


async def get_profile_deeplink(
    bot: Bot,
    **__: Any,
) -> dict[str, Any]:
    link = create_startapp_link(bot, json.dumps({"path": "/profile"}), encode=True)
    return {"profile_deeplink": link}
