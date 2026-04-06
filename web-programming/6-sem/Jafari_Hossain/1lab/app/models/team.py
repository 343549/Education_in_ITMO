import datetime as dt

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, nullable=False)

    # Внешний ключ: команда относится к проекту.
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Связь с проектом (inverse relationship).
    project: Mapped["Project"] = relationship(back_populates="teams")

    # Участники команды (many-to-many через TeamMembership).
    memberships: Mapped[list["TeamMembership"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )

    # Задачи внутри команды (one-to-many).
    tasks: Mapped[list["ProjectTask"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )

