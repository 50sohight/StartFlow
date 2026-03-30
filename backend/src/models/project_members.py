from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, VARCHAR, Uuid

import uuid

class ProjectMembersOrm(Base):
    __tablename__ = "project_members"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("projects.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(VARCHAR(30))

    project: Mapped["ProjectsOrm"] = relationship(back_populates="members")
    user: Mapped["UsersOrm"] = relationship(back_populates="project_memberships")

