from typing import Literal, cast

import fastapi
from dishka.integrations.fastapi import setup_dishka
from starlette.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from maxhack.config import load_config
from maxhack.di import make_container
from maxhack.logger import get_logger
from maxhack.utils.log_config import set_logging
from maxhack.web.errors import exception_handlers
from maxhack.web.routes import (
    auth_router,
    event_router,
    group_router,
    healthcheck_router,
    tag_router,
    user_router,
)

logger = get_logger(__name__)

tags_metadata = [
    {
        "name": "Healthcheck",
        "description": "Роут для проверки соединения приложения с базой данных",
    },
    {
        "name": "Auth",
        "description": "Роут для проверки WebAppData при запуске мини-аппа",
    },
]

description = """
### Права доступа к сущностям

Для каждой сущности предусмотрен определённый набор прав, которые, в зависимости от логики, могут назначаться различному
набору ролей. Также, помимо основного набора прав, ограничения могут быть выставлены непосредственно на уровне определённых ролей.
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
    exception_handlers=exception_handlers,
)

config = load_config()
container = make_container(config=config)
setup_dishka(container, app)

app.include_router(healthcheck_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(group_router)
app.include_router(tag_router)
app.include_router(event_router)

set_logging(
    level=cast(Literal["DEBUG", "INFO", "ERROR", "WARNING"], config.log_level),
    enable_additional_debug=config.app.additional_debug,
    app=app,
)

if config.app.cors:
    allowed_origins = ["*"] if config.app.cors_policy_disabled else config.app.cors
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
        allow_credentials=True,
    )

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
