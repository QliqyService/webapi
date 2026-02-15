import inspect

from app.services.auth import Authorization
from app.services.auth_proxy import AuthProxyClient
from app.services.base import BaseService
from app.services.postgresql import PostgreSQL
from app.services.qrcode_client import QRCodeClient
from app.services.rabbitmq import RabbitMQClient
from app.settings import SETTINGS


__all__ = ["Services"]


class Services:
    auth_proxy = AuthProxyClient(
        url=SETTINGS.AUTH_BACKEND_URL,
    )
    auth = Authorization(
        secret_key=SETTINGS.AUTH_SECRET_KEY,
        algorythm=SETTINGS.AUTH_PASSWORD_ALGORYTHM,
        login_url=SETTINGS.AUTH_LOGIN_URL,
        expires_delta=SETTINGS.AUTH_ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    database = PostgreSQL(
        username=SETTINGS.POSTGRES_USER,
        password=SETTINGS.POSTGRES_PASSWORD,
        host=SETTINGS.POSTGRES_HOST,
        port=SETTINGS.POSTGRES_PORT,
        database=SETTINGS.POSTGRES_DB,
        echo_pool=SETTINGS.POSTGRES_ECHO_POOL,
        pool_size=SETTINGS.POSTGRES_POOL_SIZE,
        connection_retry_period_sec=SETTINGS.POSTGRES_CONNECTION_RETRY_PERIOD_SEC,
        statement_timeout=SETTINGS.POSTGRES_STATEMENT_TIMEOUT,
    )
    qr_client = QRCodeClient(SETTINGS.QRCODE_SERVICE_URL)
    rabbitmq = RabbitMQClient(url=SETTINGS.RABBITMQ_URL)

    @classmethod
    def get_external_services(cls) -> list[BaseService]:
        """
        Find all class attributes with BaseService subclass
        for using start and stop methods.
        """
        external_services = []
        for _, obj in inspect.getmembers(cls):
            if issubclass(type(obj), BaseService):
                external_services.append(obj)
        return external_services
