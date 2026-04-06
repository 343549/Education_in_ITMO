import datetime as dt

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, nullable=False)
    deadline: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    # Внешний ключ на владельца проекта (создатель проекта).
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Связь “пользователь <-> проекты” (one-to-many).
    owner: Mapped["User"] = relationship(back_populates="projects")

    # Команды, участвующие в проекте (project -> teams).
    teams: Mapped[list["Team"]] = relationship(back_populates="project", cascade="all, delete-orphan")

