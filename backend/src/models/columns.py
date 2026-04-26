from typing import List

from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, VARCHAR, ForeignKey, text

import uuid


class ColumnsOrm(Base):
    __tablename__ = "columns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), server_default=text("gen_random_uuid()"), primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(VARCHAR(50))
    position: Mapped[int]

    project: Mapped["ProjectsOrm"] = relationship(back_populates="columns")
    tasks: Mapped[List["TasksOrm"]] = relationship(back_populates="column")