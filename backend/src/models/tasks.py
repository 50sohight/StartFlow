from typing import List

from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, VARCHAR, TIMESTAMP, text, ForeignKey

from datetime import datetime
import uuid


class TasksOrm(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), server_default=text("gen_random_uuid()"), primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("projects.id"))
    column_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("columns.id"))
    title: Mapped[str] = mapped_column(VARCHAR(255))
    description: Mapped[str]
    deadline: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    project: Mapped["ProjectsOrm"] = relationship(
        back_populates="tasks"
    )
    column: Mapped["ColumnsOrm"] = relationship(
        back_populates="tasks"
    )
    users: Mapped[List["TaskAssigneesOrm"]] = relationship(
        back_populates="tasks"
    )

