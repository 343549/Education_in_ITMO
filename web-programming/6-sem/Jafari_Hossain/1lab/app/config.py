import os
from functools import lru_cache

from dotenv import load_dotenv


# Загружаем переменные из `.env` (если файл существует).
load_dotenv()


@lru_cache(maxsize=1)
def get_settings():
    # Центральное место, где мы читаем настройки приложения.
    # Используется `lru_cache`, чтобы не перечитывать env на каждый запрос.
    return {
        "database_url": os.getenv(
            "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/team_finder"
        ),
        "secret_key": os.getenv("SECRET_KEY", "change_me_to_a_long_random_string"),
        "algorithm": os.getenv("ALGORITHM", "HS256"),
        "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
    }

