"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"



class AnalyzeRequest(BaseModel):
    """Request model for PR analysis."""
    repo_url: HttpUrl = Field(..., description="GitHub repository URL")
    pr_number: int = Field(..., gt=0, description="Pull request number")
    github_token: Optional[str] = Field(None, description="Optional GitHub token for private repos")
    analysis_types: Optional[List[str]] = Field(
        default=["style", "bug", "security", "performance"],
        description="Types of analysis to perform"
    )
    priority: Optional[str] = Field(default="normal", description="Task priority (low, normal, high)")


class AnalyzeResponse(BaseModel):
    """Response model for PR analysis request."""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")
    estimated_completion_time: Optional[str] = Field(None, description="Estimated completion time")


class TaskStatusResponse(BaseModel):
    """Response model for task status check."""
    task_id: str
    status: TaskStatus
    progress: Dict[str, Any] = Field(default_factory=dict)
    current_file: Optional[str] = None
    processed_files: int = 0
    total_files: int = 0
    created_at: datetime
    started_at: Optional[datetime] = None
    estimated_completion: Optional[str] = None
    error_message: Optional[str] = None