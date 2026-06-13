import uuid
from datetime import datetime
from typing import List

from sqlalchemy import TIMESTAMP, VARCHAR, ForeignKey, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class TasksOrm(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), server_default=text("gen_random_uuid()"), primary_key=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("projects.id"))
    column_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("columns.id"))
    title: Mapped[str] = mapped_column(VARCHAR(255))
    description: Mapped[str]
    deadline: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    done_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )

    project: Mapped["ProjectsOrm"] = relationship(back_populates="tasks")
    column: Mapped["ColumnsOrm"] = relationship(back_populates="tasks")
    users: Mapped[List["TaskAssigneesOrm"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )
