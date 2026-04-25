from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
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

