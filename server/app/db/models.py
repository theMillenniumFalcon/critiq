"""SQLAlchemy base model and analysis task model."""

from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class TaskStatus(str, Enum):
	"""Task status enumeration."""
	PENDING = "pending"
	PROCESSING = "processing"
	COMPLETED = "completed"
	FAILED = "failed"


class AnalysisTask(Base):
	"""Model for storing analysis task information."""
    
	__tablename__ = "analysis_tasks"
    
	id = Column(Integer, primary_key=True, index=True)
	task_id = Column(String(255), unique=True, index=True, nullable=False)
	repo_url = Column(String(500), nullable=False)
	pr_number = Column(Integer, nullable=False)
	status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    
	# Timestamps
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	updated_at = Column(DateTime(timezone=True), onupdate=func.now())
	started_at = Column(DateTime(timezone=True), nullable=True)
	completed_at = Column(DateTime(timezone=True), nullable=True)
    
	# Results and metadata
	results = Column(JSON, nullable=True)
	error_message = Column(Text, nullable=True)
	task_metadata = Column(JSON, nullable=True)
    
	# Progress tracking
	total_files = Column(Integer, default=0)
	processed_files = Column(Integer, default=0)
	current_file = Column(String(500), nullable=True)
    
	# Cost tracking
	api_calls_made = Column(Integer, default=0)
	api_calls_cached = Column(Integer, default=0)
	estimated_cost = Column(String(50), nullable=True)

