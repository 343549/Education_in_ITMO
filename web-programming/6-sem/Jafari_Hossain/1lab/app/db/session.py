from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

# Импорт моделей, чтобы SQLAlchemy зарегистрировал связи/mapper'ы.
import app.models  # noqa: E402,F401

engine = create_engine(
    settings["database_url"],
    # Для SQLite нужен check_same_thread=False при использовании в приложении.
    connect_args={"check_same_thread": False} if settings["database_url"].startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

