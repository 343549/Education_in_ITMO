import datetime as dt
from typing import Any

from jose import jwt
import bcrypt

from app.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    # bcrypt работает с байтами; в БД мы храним строку (UTF-8) результата.
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Возвращаем True/False для проверки пароля.
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        # Если хэш в базе повреждён/невалидный — считаем пароль неверным.
        return False


def create_access_token(subject: str, expires_delta_minutes: int | None = None, extra: dict[str, Any] | None = None) -> str:
    # Формируем payload JWT:
    # - sub: идентификатор пользователя (у нас email)
    # - iat: время выпуска токена
    # - exp: время истечения
    expire_minutes = expires_delta_minutes if expires_delta_minutes is not None else settings["access_token_expire_minutes"]
    now = dt.datetime.utcnow()
    expire = now + dt.timedelta(minutes=expire_minutes)

    to_encode: dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": expire}
    if extra:
        to_encode.update(extra)

    return jwt.encode(to_encode, settings["secret_key"], algorithm=settings["algorithm"])


def decode_token(token: str) -> dict[str, Any]:
    # Проверяем подпись JWT и возвращаем payload.
    return jwt.decode(token, settings["secret_key"], algorithms=[settings["algorithm"]])

