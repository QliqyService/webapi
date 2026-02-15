import random
import secrets
import string
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext


__all__ = ["Authorization"]


class Authorization:
    _crypto_manager: CryptContext
    _secret_key: str
    _algorythm: str
    _expires_delta: int
    oauth2_schema: OAuth2PasswordBearer

    def __init__(
        self,
        secret_key: str,
        algorythm: str,
        login_url: str,
        expires_delta: int,
    ):
        login_url = login_url.lstrip("/")
        self._crypto_manager = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._secret_key = secret_key
        self._algorythm = algorythm
        self._expires_delta = expires_delta

        self.oauth2_schema = OAuth2PasswordBearer(
            tokenUrl=login_url,
            auto_error=False,
        )

    @staticmethod
    def generate_random_password(length: int = 8) -> str:
        """Generate random password of letters and digits.

        Args:
            length (int, optional): password length. Defaults to 8.

        Returns:
            str: random password
        """
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choice(characters) for _ in range(length))
        return random_string

    def get_password_hash(self, password: str) -> str:
        """Get hash of the provided password.

        Args:
            password (str): password

        Returns:
            str: password hash
        """
        return self._crypto_manager.hash(password)

    def create_jwt(
        self,
        payload: dict[str, str],
        expires_delta: int | None = None,
        secret_key: str | None = None,
    ) -> str:
        """Create JWT

        Args:
            payload (dict[str, str]): JWT payload
            expires_delta (int | None, optional): expiration time in seconds. Defaults to None.
            secret_key (str | None, optional): secret key for signing. Defaults to None.

        Returns:
            str: JWT token
        """
        expires_delta = expires_delta or self._expires_delta
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)

        payload["exp"] = expire

        secret_key = secret_key or self._secret_key

        encoded_jwt = jwt.encode(
            claims=payload,
            key=secret_key,
            algorithm=self._algorythm,
        )
        return encoded_jwt

    def decode_jwt(
        self,
        token: str,
        secret_key: str | None = None,
        audience: str | None = None,
    ) -> dict:
        """Decode JWT token and get JWT payload.

        Args:
            token (str): JWT access token
            secret_key (str | None): secret key for signing. Defaults to None.
            audience (str | None): audience for JWT. Defaults to None.

        Returns:
            JwtPayload: JWT payload with user ID and expiration time
        """
        secret_key = secret_key or self._secret_key

        payload = jwt.decode(
            token=token,
            key=secret_key,
            algorithms=self._algorythm,
            audience=audience,
        )
        return payload

    @staticmethod
    def generate_api_key() -> str:
        """Сгенерировать API ключ.

        Генерирует криптографически стойкий API ключ используя uuid4 и secrets.
        Формат: prefix_uuid4_suffix, где prefix и suffix - случайные строки.

        Returns:
            str: сгенерированный API ключ
        """
        prefix = secrets.token_urlsafe(8)
        suffix = secrets.token_hex(8)
        unique_id = str(uuid.uuid4())

        return f"{prefix}_{unique_id}_{suffix}"
