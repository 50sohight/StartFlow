from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, VARCHAR, ForeignKey, DateTime, func, Computed, text
from datetime import datetime
import uuid


class LinksOrm(Base):
    __tablename__ = "links"

    link: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("projects.id"))

    created_by: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("users.id"))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )

    used_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), ForeignKey("users.id"), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["ProjectsOrm"] = relationship(back_populates="links")
    creator: Mapped["UsersOrm"] = relationship(foreign_keys=[created_by], back_populates="created_links")
    user_who_used: Mapped["UsersOrm | None"] = relationship(foreign_keys=[used_by], back_populates="used_links")