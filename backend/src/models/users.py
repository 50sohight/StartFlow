from typing import List
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import VARCHAR, Uuid, text
import uuid


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, server_default=text("gen_random_uuid()"))
    login: Mapped[str] = mapped_column(VARCHAR(100), unique=True)
    password_hash: Mapped[str] = mapped_column(VARCHAR(255))
    fullname: Mapped[str] = mapped_column(VARCHAR(100))

    project_memberships: Mapped[List["ProjectMembersOrm"]] = relationship(back_populates="user")
    tasks: Mapped[List["TaskAssigneesOrm"]] = relationship(back_populates="user")
    
    created_links: Mapped[List["LinksOrm"]] = relationship(foreign_keys="LinksOrm.created_by", back_populates="creator")
    used_links: Mapped[List["LinksOrm"]] = relationship(foreign_keys="LinksOrm.used_by", back_populates="user_who_used")