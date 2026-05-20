from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from db.base import Base


class AspectDB(Base):
    __tablename__ = "aspects"
    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_aspect_name_user"),)

    aspect_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user = relationship("UserDB", back_populates="aspects")
