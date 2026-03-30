from typing import List
from database import Base  # ИСПРАВЛЕНО
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, Uuid, VARCHAR, Text, TIMESTAMP, text
import uuid
from datetime import datetime


class ProjectsOrm(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(VARCHAR(100))
    description: Mapped[str] = mapped_column(Text())
    status: Mapped[str] = mapped_column(VARCHAR(20))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    members: Mapped[List["ProjectMembersOrm"]] = relationship(back_populates="project")
    columns: Mapped[List["ColumnsOrm"]] = relationship(back_populates="project")
    tasks: Mapped[List["TasksOrm"]] = relationship(back_populates="project")
    

    links: Mapped[List["LinksOrm"]] = relationship(back_populates="project")

    __table_args__ = (
        CheckConstraint("status IN ('активный', 'архивный')", name="check_status_valid"),
    )