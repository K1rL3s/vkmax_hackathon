# Бэкенд

Состоит из веб-апи fastapi, бота maxo, шедулера taskiq, очереди nats, бд psql и redis.

## Docker

### Локальный запуск

1. Всё внутри докера:
    ```bash
    docker compose -f docker-compose.local.yml up --build -d
    ```
    ```bash
    docker compose -f docker-compose.local.yml up --build -d api
    ```
2. Запуск из IDE:
    1. Поднять psql и redis:
        ```bash
        docker compose -f docker-compose.local.yml --env-file=.env run --remove-orphans -d -p 5432:5432 database
        docker compose -f docker-compose.local.yml --env-file=.env run --remove-orphans -d -p 6379:6379 redis
        ```
    2. Запускать из `MAX_task_magager/backend`:
        ```bash
        python -m maxhack.bot
        python -m maxhack.web
        python -m maxhack.scheduler
        python -m maxhack.broker
        ```
