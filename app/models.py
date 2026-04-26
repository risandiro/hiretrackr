from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    is_verified = Column(Boolean, nullable=False, default=False, server_default="false")
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_sent_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cv_groups = relationship(
        "CVGroup",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(CVGroup.created_at)",
    )


class CVGroup(Base):
    __tablename__ = "cv_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user = relationship("User", back_populates="cv_groups")
    versions = relationship(
        "CVVersion",
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="desc(CVVersion.uploaded_at)",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_cv_groups_user_name"),
    )


class CVVersion(Base):
    __tablename__ = "cv_versions"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("cv_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    filename_original = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)

    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    group = relationship("CVGroup", back_populates="versions")
    
    __table_args__ = (
        UniqueConstraint("group_id", "version_number", name="uq_cv_versions_group_version"),
    )