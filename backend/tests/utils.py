from datetime import datetime
from typing import Any

from httpx import AsyncClient


async def auth_user(
    client: AsyncClient,
    web_app_data: str,
) -> dict[str, Any]:
    """Создает/авторизует пользователя через API GET /auth с WebAppData."""

    resp = await client.get(
        "/auth",
        params={"WebAppData": web_app_data},
    )

    user = await client.post()

    assert resp.status_code == 200
    auth_data = resp.json()

    # Извлекаем данные из WebAppData
    user_info = auth_data["user"]
    chat_info = auth_data["chat"]

    # Пытаемся получить пользователя из БД
    # resp = await client.get("/users/me", headers={"WebAppData": web_app_data})
    #
    # # Если пользователь не найден (404), создаем его через POST /users
    # if resp.status_code == 404:
    #     create_data = {
    #         "max_id": user_info["id"],
    #         "max_chat_id": chat_info["id"],
    #         "first_name": user_info["first_name"],
    #         "last_name": user_info.get("last_name") or "",
    #         "phone": None,
    #         "timezone": 0,
    #     }
    #     resp = await client.post("/users", json=create_data)
    #     assert resp.status_code == 201

    # # Получаем полные данные пользователя из БД
    # resp = await client.get("/users/me", headers={"WebAppData": web_app_data})
    # assert resp.status_code == 200
    # user_data = resp.json()

    return user_info


async def create_group(
    client: AsyncClient,
    web_app_data: str,
    name: str = "Test Group",
    description: str | None = "Test Description",
    timezone: int | None = None,
) -> dict[str, Any]:
    """Создает группу через API POST /groups."""
    data: dict[str, Any] = {
        "name": name,
        "description": description,
    }
    if timezone is not None:
        data["timezone"] = timezone
    resp = await client.post(
        "/groups",
        json=data,
        headers={"WebAppData": web_app_data},
    )
    assert resp.status_code == 201
    return resp.json()


async def create_tag(
    client: AsyncClient,
    web_app_data: str,
    group_id: int,
    name: str = "Test Tag",
    description: str | None = "Test Tag Description",
    color: str = "#FF0000",
) -> dict[str, Any]:
    """Создает тег через API POST /groups/{group_id}/tags."""
    data: dict[str, Any] = {
        "name": name,
        "color": color,
    }
    if description is not None:
        data["description"] = description
    resp = await client.post(
        f"/groups/{group_id}/tags",
        json=data,
        headers={"WebAppData": web_app_data},
    )
    assert resp.status_code == 201
    return resp.json()


async def assign_tag_to_user(
    client: AsyncClient,
    web_app_data: str,
    group_id: int,
    user_id: int,
    tag_id: int,
) -> None:
    """Назначает тег пользователю через API POST /groups/{group_id}/tags/users."""
    data = {
        "user_id": user_id,
        "tag_id": tag_id,
    }
    resp = await client.post(
        f"/groups/{group_id}/tags/users",
        json=data,
        headers={"WebAppData": web_app_data},
    )
    assert resp.status_code == 204


async def create_event(
    client: AsyncClient,
    web_app_data: str,
    group_id: int,
    title: str = "Test Event",
    description: str | None = "Test Event Description",
    cron_date: datetime | None = None,
    every_day: bool = False,
    every_week: bool = False,
    every_month: bool = False,
    participants_ids: list[int] | None = None,
    tags_ids: list[int] | None = None,
) -> dict[str, Any]:
    """Создает событие через API POST /events."""
    if cron_date is None:
        cron_date = datetime.now()
    data: dict[str, Any] = {
        "title": title,
        "type": "event",
        "group_id": group_id,
        "cron": {
            "date": cron_date.isoformat(),
            "every_day": every_day,
            "every_week": every_week,
            "every_month": every_month,
        },
        "participants_ids": participants_ids or [],
        "tags_ids": tags_ids or [],
        "minutes_before": [],
    }
    if description is not None:
        data["description"] = description
    resp = await client.post(
        "/events",
        json=data,
        headers={"WebAppData": web_app_data},
    )
    assert resp.status_code == 201
    return resp.json()


async def add_tag_to_event(
    client: AsyncClient,
    web_app_data: str,
    event_id: int,
    tag_ids: list[int],
) -> None:
    """Добавляет тег к событию через API POST /events/{event_id}/tags."""
    data = {
        "tag_ids": tag_ids,
    }
    resp = await client.post(
        f"/events/{event_id}/tags",
        json=data,
        headers={"WebAppData": web_app_data},
    )
    assert resp.status_code == 204


async def add_user_to_event(
    client: AsyncClient,
    web_app_data: str,
    event_id: int,
    user_ids: list[int],
) -> None:
    """Добавляет пользователя к событию через API POST /events/{event_id}/users."""
    data = {
        "user_ids": user_ids,
    }
    resp = await client.post(
        f"/events/{event_id}/users",
        json=data,
        headers={"WebAppData": web_app_data},
    )
    assert resp.status_code == 204
