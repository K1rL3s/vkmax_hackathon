import os
from collections.abc import AsyncIterable
from pathlib import Path

import fastapi
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy.ext.asyncio import AsyncEngine

from maxhack.config import Config, load_config
from maxhack.database.models import BaseAlchemyModel
from maxhack.di import make_container
from maxhack.web.main import main

os.environ["SERVER_PORT"] = "5001"
os.environ["POSTGRES_CONN"] = "postgres://root:root@127.0.0.1:8889/test"

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
async def reinit_database(dishka_container: AsyncContainer) -> AsyncIterable[None]:
    engine = await dishka_container.get(AsyncEngine)

    yield

    async with engine.begin() as conn:
        for table in reversed(BaseAlchemyModel.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture(scope="session")
async def client(app: fastapi.FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def config() -> Config:

    return load_config((Path(__file__).parent.parent / ".env.test").resolve())


@pytest.fixture(scope="session")
async def app(config: Config) -> fastapi.FastAPI:
    return main(config)


@pytest.fixture(scope="session")
async def dishka_container(
    app: fastapi.FastAPI,
    config: Config,
) -> AsyncIterable[AsyncContainer]:
    container_ = make_container(config=config)
    setup_dishka(container_, app)

    yield container_
    await container_.close()


@pytest.fixture
async def request_dishka_container(
    dishka_container: AsyncContainer,
) -> AsyncIterable[AsyncContainer]:
    async with dishka_container() as request_container:
        yield request_container
