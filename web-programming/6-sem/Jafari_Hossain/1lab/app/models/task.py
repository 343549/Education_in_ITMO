import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProjectTask(Base):
    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Простой статус задачи (на учебную/демо часть; позже можно Enum).
    status: Mapped[str] = mapped_column(String(50), default="todo", nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, nullable=False)
    due_date: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    # Внешний ключ: задача принадлежит команде.
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Связь back_populates с `Team.tasks`.
    team: Mapped["Team"] = relationship(back_populates="tasks")

