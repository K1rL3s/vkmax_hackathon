from typing import Any

from maxo.dialogs import DialogManager


async def on_start_update_dialog_data(_: Any, dialog_manager: DialogManager) -> None:
    if isinstance(dialog_manager.start_data, dict):
        dialog_manager.dialog_data.update(dialog_manager.start_data)
