from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, ForeignKey

import uuid


class TaskAssigneesOrm(Base):
    __tablename__ = "task_assignees"

    task_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("tasks.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("users.id"), primary_key=True)

    task: Mapped["TasksOrm"] = relationship(back_populates="users")
    user: Mapped["UsersOrm"] = relationship(back_populates="tasks")

