#
#   Imports
#

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from enum import Enum

# Perso

#
#   Enums
#

class Env(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

#
#   Config
#

class Settings(BaseSettings):
    """
        Settings of the app using Pydantic Settings.
    """

    #
    #   Base
    #
    
    APP_NAME: str = Field(
        ...,
        description="The name of the application"
    )
    APP_VERSION: str = Field(
        ...,
        description="The version of the application"
    )
    APP_PREFIX: str = Field(
        default="/api",
        description="The prefix of the API routes of the application"
    )
    APP_ENV: Env = Field(
        default=Env.DEVELOPMENT,
        description="The environment of the application"
    )
    APP_LOG_LEVEL: LogLevel = Field(
        default=LogLevel.INFO,
        description="The level of the application logs"
    )

    #
    #   Security
    #
    
    CORS_ALLOW_ORIGINS_PROD: list[str] = Field(
        ...,
        description="The origins allowed to access the API in production"
    )

    #
    #   DB
    #

    DB_STRING: str = Field(
        ...,
        min_length=1,
        description="The string to connect to the database"
    )
    DB_NAME: str = Field(
        default="nycbikes",
        description="The name of the database"
    )

    #
    #   Config
    #
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="forbid"
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()  # type: ignore[call-arg]