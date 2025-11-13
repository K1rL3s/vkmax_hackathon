from typing import Any, TypeVar

from maxo.dialogs import DialogManager
from maxo.dialogs.widgets.common import WhenCondition
from maxo.dialogs.widgets.common.items import ItemsGetterVariant
from maxo.dialogs.widgets.kbd import Select
from maxo.dialogs.widgets.text import Text
from maxo.types.link_keyboard_button import LinkKeyboardButton

T = TypeVar("T")


class UrlSelect(Select):
    def __init__(
        self,
        text: Text,
        url: Text,
        id: str,
        items: ItemsGetterVariant,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(
            id=id,
            when=when,
            text=text,
            items=items,
            item_id_getter=str,
            type_factory=str,
            on_click=None,
        )
        self.url = url

    async def _render_button(
        self,
        pos: int,
        item: Any,
        target_item: Any,
        data: dict,
        manager: DialogManager,
    ) -> LinkKeyboardButton:
        data = {
            "data": data,
            "item": item,
            "target_item": target_item,
            "pos": pos + 1,
            "pos0": pos,
        }
        return LinkKeyboardButton(
            text=await self.text.render_text(data, manager),
            url=await self.url.render_text(data, manager),
        )
