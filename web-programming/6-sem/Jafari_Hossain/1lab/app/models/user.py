import datetime as dt

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # Основные поля пользователя.
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, nullable=False)

    # One-to-many: пользователь создаёт проекты.
    projects: Mapped[list["Project"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

    # Many-to-many через ассоциативную таблицу `user_skills`:
    # у связи есть дополнительное поле `proficiency`.
    user_skills: Mapped[list["UserSkill"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Many-to-many через ассоциативную таблицу `team_memberships`:
    # у связи есть дополнительное поле `role`.
    team_memberships: Mapped[list["TeamMembership"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

