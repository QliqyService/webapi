from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.logger import CustomLogger


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppStand(StrEnum):
    DEV = "dev"
    RC = "rc"
    PROD = "prod"
    DEMO = "demo"
    TEST = "tests"
    LOCAL = "local"


class ServiceName(StrEnum):
    WEBAPI = "webapi"
    QR_CODE = "qrcode_generator"
    TELEGRAM = "telegram"
    MAIL = "mail"


class _Settings(BaseSettings):
    """General service settings"""

    ROOT_DIR: Path = Path(__file__).parent.parent
    APP_DIR: Path = ROOT_DIR / "app"
    TEMPLATES_DIR: Path = APP_DIR / "templates"

    APP_TITLE: str = "Qliqy | WebAPI"
    APP_WEBSITE: str = "https://qliqy.io/api/v1/docs"
    APP_DESCRIPTION: str = f"""
# Introduction
{APP_TITLE} API is a [RESTful](https://en.wikipedia.org/wiki/REST) API that provides programmatic methods to access and modify data on the {APP_TITLE} platform.
The API is hosted at [{APP_WEBSITE}]({APP_WEBSITE}) and follows standard REST practices.

Requests are made with standard HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) to documented URI endpoints with primarily `application/json` content type.

Responses include standard HTTP response codes (`200`, `201`, `202`, `204`, `400`, `401`, `404`, etc) and JSON encoded body, where applicable. Errors are also represented with a JSON object in the response body.

> NOTE: The {APP_TITLE} API is still in development mode. While stability and compatibility will be carefully maintained as much as possible, changes will likely be introduced without notice.
However, breaking changes will always be introduced with a version change and/or prior communication from the support team. Please reach out to your point of contact at {APP_TITLE} to provide feedback.
"""

    APP_DEBUG: bool = False
    APP_PUBLIC_PATH: str | None = None
    APP_STAND: AppStand = AppStand.LOCAL
    APP_RELEASE: str = "not-set"
    APP_NAME: ServiceName = ServiceName.WEBAPI

    # Auth backend
    AUTH_BACKEND_URL: str = "https://app.qliqy.io/auth"
    AUTH_SECRET_KEY: str = "key"
    AUTH_PASSWORD_ALGORYTHM: str = "HS256"
    AUTH_LOGIN_URL: str = "v1/auth/login"
    AUTH_ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7 * 2  # 2 weeks

    # Common
    REDIRECT_URL: str = "https://app.qliqy.io/"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_ECHO_POOL: str | bool = False
    POSTGRES_CONNECTION_RETRY_PERIOD_SEC: float = 5.0
    POSTGRES_STATEMENT_TIMEOUT: int = 60000
    FRONTEND_BASE_URL: str = "http://localhost:8001"
    QRCODE_SERVICE_URL: str = "http://qrcode-generator:8000"
    FORMS_PUBLIC_BASE_URL: str | None = None
    FORMS_PUBLIC_LOCAL_URL: str = "http://localhost:8001/public/forms"
    FORMS_PUBLIC_DOMAIN_URL: str = "https://qliqy.org/public/forms"
    PAGES_PREFIX: str = "qliqy"
    S3_ENDPOINT: str
    S3_BUCKET: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_REGION: str = "us-east-1"
    S3_FORCE_PATH_STYLE: bool = True
    S3_PRESIGN_EXPIRES: int = 900

    @property
    def POSTGRES_URL(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    @property
    def RABBITMQ_URL(self):
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}?name={self.APP_NAME}"

    @staticmethod
    def configure_logging():
        """Configure level and format of logging"""
        return CustomLogger.make_logger()

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


@lru_cache
def get_settings(env_file: str = ".env") -> _Settings:
    return _Settings(_env_file=env_file)


SETTINGS: Final[_Settings] = get_settings()
