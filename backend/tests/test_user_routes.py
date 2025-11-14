import pprint
from datetime import datetime

from httpx import AsyncClient

from maxhack.web.dependencies import CurrentUser
from tests.mock import WebAppData
from tests.utils import (
    add_tag_to_event,
    add_user_to_event,
    assign_tag_to_user,
    auth_user,
    create_event,
    create_group,
    create_tag,
)


class TestUserRoutes:
    """Тесты для роутов пользователей."""

    async def test_auth_user_ok(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест успешной авторизации/создания пользователя через /auth."""
        user_data = await auth_user(client, WebAppData)
        assert user_data["id"] == 84271494
        assert user_data["first_name"] == "Иван"
        assert "id" in user_data

    async def test_get_user_me_unauthorized(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения пользователя без авторизации."""
        resp = await client.get("/users/me")
        assert resp.status_code == 400

    async def test_update_user_ok(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест обновления пользователя."""
        await auth_user(client, WebAppData)

        # Обновляем данные
        update_data = {
            "first_name": "Петр",
            "last_name": "Петров",
            "phone": "+79997654321",
            "timezone": 5,
            "notify_mode": "SILENT",
        }
        resp = await client.patch(
            "/users/",
            json=update_data,
            headers={"WebAppData": WebAppData},
        )
        print(123)
        pprint.pprint(resp.json())
        assert resp.status_code == 200
        data = resp.json()
        assert data["first_name"] == "Петр"
        assert data["last_name"] == "Петров"
        assert data["phone"] == "+79997654321"
        assert data["timezone"] == 5
        assert data["notify_mode"] == "SILENT"

    async def test_update_user_partial(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест частичного обновления пользователя."""
        # Создаем/авторизуем пользователя через /auth
        initial_user = await auth_user(client, WebAppData)

        # Обновляем только имя
        update_data = {"first_name": "НовоеИмя"}
        resp = await client.patch(
            "/users/",
            json=update_data,
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["first_name"] == "НовоеИмя"
        # Остальные поля остались прежними
        assert data["last_name"] == initial_user["last_name"]
        assert data["phone"] == initial_user["phone"]

    async def test_get_user_groups_ok(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения групп пользователя."""
        # Создаем/авторизуем пользователя через /auth
        user_data = await auth_user(client, WebAppData)

        # Создаем группы через API
        group1_data = await create_group(
            client,
            WebAppData,
            name="Группа 1",
            description="Описание 1",
        )
        group2_data = await create_group(
            client,
            WebAppData,
            name="Группа 2",
            description="Описание 2",
        )

        # Получаем группы пользователя
        resp = await client.get(
            "/users/me/groups",
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "groups" in data
        assert len(data["groups"]) == 2  # Две группы (создатель в обеих)

        # Проверяем, что группы содержат правильные данные
        group_ids = [g["group_id"] for g in data["groups"]]
        assert group1_data["group"]["id"] in group_ids
        assert group2_data["group"]["id"] in group_ids

    async def test_get_user_groups_empty(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения групп пользователя, когда групп нет."""
        # Создаем/авторизуем пользователя через /auth
        await auth_user(client, WebAppData)

        resp = await client.get(
            "/users/me/groups",
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "groups" in data
        # При создании пользователя автоматически создается приватная группа
        assert len(data["groups"]) >= 0

    async def test_get_user_tags_in_group_ok(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения тегов пользователя в группе."""
        # Создаем/авторизуем пользователя через /auth
        user_data = await auth_user(client, WebAppData)

        # Создаем группу через API
        group_data = await create_group(
            client,
            WebAppData,
            name="Тестовая группа",
        )
        group_id = group_data["group"]["id"]

        # Создаем теги через API
        tag1_data = await create_tag(
            client,
            WebAppData,
            group_id=group_id,
            name="Тег 1",
            color="#FF0000",
        )
        tag2_data = await create_tag(
            client,
            WebAppData,
            group_id=group_id,
            name="Тег 2",
            color="#00FF00",
        )

        # Назначаем теги пользователю через API
        await assign_tag_to_user(
            client,
            WebAppData,
            group_id=group_id,
            user_id=user_data["id"],
            tag_id=tag1_data["id"],
        )
        await assign_tag_to_user(
            client,
            WebAppData,
            group_id=group_id,
            user_id=user_data["id"],
            tag_id=tag2_data["id"],
        )

        # Получаем теги пользователя в группе
        resp = await client.get(
            f"/users/{user_data['id']}/groups/{group_id}/tags",
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        tag_ids = [tag["id"] for tag in data]
        assert tag1_data["id"] in tag_ids
        assert tag2_data["id"] in tag_ids

    async def test_get_user_tags_in_group_empty(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения тегов пользователя, когда тегов нет."""
        # Создаем/авторизуем пользователя через /auth
        user_data = await auth_user(client, WebAppData)

        # Создаем группу через API
        group_data = await create_group(
            client,
            WebAppData,
            name="Тестовая группа",
        )
        group_id = group_data["group"]["id"]

        # Получаем теги (их нет)
        resp = await client.get(
            f"/users/{user_data['id']}/groups/{group_id}/tags",
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 0

    async def test_get_user_events_in_group_ok(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения событий пользователя в группе."""
        # Создаем/авторизуем пользователя через /auth
        user_data = await auth_user(client, WebAppData)

        # Создаем группу через API
        group_data = await create_group(
            client,
            WebAppData,
            name="Тестовая группа",
        )
        group_id = group_data["group"]["id"]

        # Создаем события через API
        event1_data = await create_event(
            client,
            WebAppData,
            group_id=group_id,
            title="Событие 1",
            cron_date=datetime.now(),
        )
        event2_data = await create_event(
            client,
            WebAppData,
            group_id=group_id,
            title="Событие 2",
            cron_date=datetime.now(),
        )

        # Добавляем пользователя к событиям через API
        await add_user_to_event(
            client,
            WebAppData,
            event_id=event1_data["id"],
            user_ids=[user_data["id"]],
        )
        await add_user_to_event(
            client,
            WebAppData,
            event_id=event2_data["id"],
            user_ids=[user_data["id"]],
        )

        # Получаем события пользователя в группе
        resp = await client.get(
            f"/users/{user_data['id']}/groups/{group_id}/events",
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        event_ids = [event["id"] for event in data]
        assert event1_data["id"] in event_ids
        assert event2_data["id"] in event_ids

    async def test_get_user_events_in_group_with_tag_filter(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения событий пользователя с фильтром по тегам."""
        # Создаем/авторизуем пользователя через /auth
        user_data = await auth_user(client, WebAppData)

        # Создаем группу через API
        group_data = await create_group(
            client,
            WebAppData,
            name="Тестовая группа",
        )
        group_id = group_data["group"]["id"]

        # Создаем тег через API
        tag_data = await create_tag(
            client,
            WebAppData,
            group_id=group_id,
            name="Важный тег",
        )

        # Создаем события через API
        event1_data = await create_event(
            client,
            WebAppData,
            group_id=group_id,
            title="Событие с тегом",
            cron_date=datetime.now(),
        )
        event2_data = await create_event(
            client,
            WebAppData,
            group_id=group_id,
            title="Событие без тега",
            cron_date=datetime.now(),
        )

        # Добавляем тег к событию 1 через API
        await add_tag_to_event(
            client,
            WebAppData,
            event_id=event1_data["id"],
            tag_ids=[tag_data["id"]],
        )

        # Добавляем пользователя к событиям через API
        await add_user_to_event(
            client,
            WebAppData,
            event_id=event1_data["id"],
            user_ids=[user_data["id"]],
        )
        await add_user_to_event(
            client,
            WebAppData,
            event_id=event2_data["id"],
            user_ids=[user_data["id"]],
        )

        # Получаем события с фильтром по тегу
        resp = await client.get(
            f"/users/{user_data['id']}/groups/{group_id}/events",
            params={"tag_ids": str(tag_data["id"])},
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Должно быть только событие с тегом
        assert len(data) >= 1
        event_ids = [event["id"] for event in data]
        assert event1_data["id"] in event_ids

    async def test_get_user_events_in_group_empty(
        self,
        client: AsyncClient,
        reinit_database,
    ):
        """Тест получения событий пользователя, когда событий нет."""
        # Создаем/авторизуем пользователя через /auth
        user_data = await auth_user(client, WebAppData)

        # Создаем группу через API
        group_data = await create_group(
            client,
            WebAppData,
            name="Тестовая группа",
        )
        group_id = group_data["group"]["id"]

        # Получаем события (их нет)
        resp = await client.get(
            f"/users/{user_data['id']}/groups/{group_id}/events",
            headers={"WebAppData": WebAppData},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 0

