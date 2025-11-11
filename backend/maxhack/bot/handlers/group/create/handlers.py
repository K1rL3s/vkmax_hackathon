import html
from typing import Any

from dishka import FromDishka

from maxhack.bot.states import Groups, GroupsCreate
from maxhack.core.group.service import GroupService
from maxhack.infra.database.models import UserModel
from maxo.dialogs import DialogManager, ShowMode, StartMode
from maxo.dialogs.integrations.dishka import inject


def validate_group_name(text: str) -> str:
    name = html.escape(text.strip())
    if not name:
        raise ValueError("Пустое название группы")
    if len(name) > 64:
        raise ValueError("Слишком большое название группы")
    return name


def validate_group_description(text: str) -> str:
    description = html.escape(text.strip())
    if not description:
        raise ValueError("Пустое описание группы")
    if len(description) > 64:
        raise ValueError("Слишком большое описание группы")
    return description


def validate_group_timezone(text: str) -> int:
    try:
        timezone = int(text)
    except ValueError as e:
        raise ValueError("Таймзона должна быть числом в минутах") from e

    if abs(timezone) > 24 * 60:
        raise ValueError("Разница таймзоны должна быть в пределах суток")

    return timezone


async def on_group_name(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    name: str,
) -> None:
    dialog_manager.dialog_data["group_name"] = name
    await dialog_manager.switch_to(
        state=GroupsCreate.wait_description,
        show_mode=ShowMode.SEND,
    )


async def on_group_description(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    description: str,
) -> None:
    dialog_manager.dialog_data["group_description"] = description
    await dialog_manager.switch_to(
        state=GroupsCreate.wait_timezone,
        show_mode=ShowMode.SEND,
    )


async def on_group_timezone(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    timezone: int,
) -> None:
    dialog_manager.dialog_data["group_timezone"] = timezone
    await dialog_manager.switch_to(
        state=GroupsCreate.confirm,
        show_mode=ShowMode.SEND,
    )


@inject
async def on_create_confirm(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    group_service: FromDishka[GroupService],
) -> None:
    current_user: UserModel = dialog_manager.middleware_data["current_user"]
    name: str = dialog_manager.dialog_data["group_name"]
    description: str | None = dialog_manager.dialog_data.get("group_description")
    timezone: int | None = dialog_manager.dialog_data.get("group_timezone")

    group = await group_service.create_group(
        current_user.id,
        name,
        description,
        timezone,
    )
    await dialog_manager.start(
        state=Groups.one,
        show_mode=ShowMode.SEND,
        mode=StartMode.RESET_STACK,
        data={"group_id": group.id},
    )
