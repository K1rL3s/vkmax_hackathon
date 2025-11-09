import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True, kw_only=True)
class MaxConfig:
    token: str


@dataclass(slots=True, frozen=True, kw_only=True)
class DbConfig:
    protocol: str = "postgresql+psycopg"
    host: str
    port: int
    user: str
    password: str
    db_name: str

    @property
    def uri(self) -> str:
        return f"{self.protocol}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


@dataclass(slots=True, frozen=True, kw_only=True)
class RedisConfig:
    host: str
    port: int
    password: str | None = None
    database: int = 0

    @property
    def uri(self) -> str:
        password = "" if self.password is None else f":{self.password}@"
        return f"redis://{password}{self.host}:{self.port}/{self.database}"


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    max: MaxConfig
    db: DbConfig
    redis: RedisConfig

    log_level: str


def load_config(env: str | Path | None = None) -> Config:
    if env:
        from dotenv import load_dotenv

        load_dotenv(env)

    return Config(
        max=MaxConfig(token=os.environ["MAX_TOKEN"]),
        db=DbConfig(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            db_name=os.environ["DB_NAME"],
        ),
        redis=RedisConfig(
            host=os.environ["REDIS_HOST"],
            port=int(os.environ["REDIS_PORT"]),
            password=os.getenv("REDIS_PASSWORD", None),
            database=int(os.getenv("REDIS_DB", 0)),
        ),
        log_level=os.getenv("LOG_LEVEL", "DEBUG"),
    )
