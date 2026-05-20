from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import func

from db.base import Base

from models.user import UserDB


class AnalysisDB(Base):
    __tablename__ = "analyses"

    analysis_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    user = relationship("UserDB", back_populates="analyses")
    aspect_results = relationship("AspectAnalysisDB", back_populates="analysis", cascade="all, delete-orphan")
    without_aspect_results = relationship( "WithoutAspectAnalysisDB", back_populates="analysis", cascade="all, delete-orphan")


class AspectAnalysisDB(Base):
    __tablename__ = "aspect_based_analyses"

    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(String(512), nullable=False)
    aspect = Column(String(64), nullable=False)
    label = Column(String(64), nullable=False)
    score = Column(Float, nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.analysis_id"), nullable=False)

    analysis = relationship("AnalysisDB", back_populates="aspect_results")


class WithoutAspectAnalysisDB(Base):
    __tablename__ = "without_aspect_analyses"

    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(String(512), nullable=False)
    label = Column(String(64), nullable=False)
    score = Column(Float, nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.analysis_id"), nullable=False)

    analysis = relationship("AnalysisDB", back_populates="without_aspect_results")