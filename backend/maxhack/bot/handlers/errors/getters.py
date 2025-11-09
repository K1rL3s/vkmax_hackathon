from typing import Any

from maxo.dialogs import DialogManager


async def get_error_reason(dialog_manager: DialogManager, **__: Any) -> dict[str, Any]:
    return {"reason": (dialog_manager.start_data or {}).get("reason")}
