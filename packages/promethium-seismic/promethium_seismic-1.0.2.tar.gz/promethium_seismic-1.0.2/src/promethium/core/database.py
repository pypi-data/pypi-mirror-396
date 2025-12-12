from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, Text
from datetime import datetime
from typing import Optional, Dict, Any
from promethium.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class Dataset(Base):
    """
    Registry for seismic datasets.
    """
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    file_path: Mapped[str] = mapped_column(String(1024))
    format: Mapped[str] = mapped_column(String(50)) # SEGY, SAC, etc.
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="dataset")

class Job(Base):
    """
    Record of a processing/recovery job.
    """
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True) # UUID
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    algorithm: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="QUEUED") # QUEUED, RUNNING, COMPLETED, FAILED
    params: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    result_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    dataset = relationship("Dataset", back_populates="jobs")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
