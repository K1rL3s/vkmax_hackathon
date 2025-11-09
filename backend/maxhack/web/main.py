from typing import Literal, cast

import fastapi
from dishka.integrations.fastapi import setup_dishka
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from maxhack.config import load_config
from maxhack.di import make_container
from maxhack.utils.log_config import set_logging
from maxhack.web.routes import (
    event_router,
    group_router,
    healthcheck_router,
    tag_router,
    user_router,
)

tags_metadata = [
    {
        "name": "Healthcheck",
        "description": "Роут для проверки соединения приложения с базой данных",
    },
]

description = """
### Права доступа к сущностям

Для каждой сущности предусмотрен определённый набор прав, которые, в зависимости от логики, могут назначаться различному
набору ролей. Также, помимо основного набора прав, ограничения могут быть выставлены непосредственно на уровне определённых ролей.

### Тестирование
Для тестирования запросов к API существует служебный токен (обладающий правами суперадминистратора), который можно сконфигурировать в
конфиг-переменной ``test_token``
"""
app = fastapi.FastAPI(
    title="Таск трекер для МАКС",
    description=description,
    version="0.1.0",
    openapi_tags=sorted(tags_metadata, key=lambda i: i["name"]),
    swagger_ui_parameters={
        "docExpansion": "none",
        "displayRequestDuration": "true",
        "syntaxHighlight.theme": "obsidian",
        "tryItOutEnabled": "true",
        "requestSnippetsEnabled": "true",
    },
)

config = load_config()
container = make_container(config=config)
setup_dishka(container, app)

app.include_router(healthcheck_router)
app.include_router(user_router)
app.include_router(group_router)
app.include_router(tag_router)
app.include_router(event_router)

set_logging(
    level=cast(Literal["DEBUG", "INFO", "ERROR", "WARNING"], config.log_level),
    enable_additional_debug=config.app.additional_debug,
    app=app,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config.app.secret.encode("utf-8").hex(),
)

default_errors = {
    401: {"description": "Unauthorized"},
    403: {"description": "No permission"},
    404: {"description": "Object not found"},
    409: {"description": "Collision occurred. Entity already exists"},
    410: {"description": "Already Expired"},
}

# Todo: Сделать обработтчики ошибок
# add_exception_handlers(app)

if config.app.cors_policy_disabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
        allow_credentials=True,
    )

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
