"""Pydantic models for the server API."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


class FormatEnum(str, Enum):
    """Supported output formats."""

    markdown = "markdown"
    json = "json"
    html = "html"
    pdf = "pdf"


class AnalysisRequest(BaseModel):
    """Request model for repository analysis."""

    repo_url: HttpUrl = Field(..., description="GitHub repository URL to analyze")
    model: Optional[str] = Field(None, description="LLM model to use for analysis")
    nocache: bool = Field(False, description="Skip cache and force re-analysis")
    github_token: Optional[str] = Field(None, description="GitHub API token")
    format: FormatEnum = Field(FormatEnum.markdown, description="Output format")


class AnalysisStatus(str, Enum):
    """Analysis status types."""

    generating = "generating"
    available = "available"
    error = "error"


class AnalysisResponse(BaseModel):
    """Response model for analysis requests."""

    status: AnalysisStatus = Field(..., description="Current status of the analysis")
    retry_after: Optional[datetime] = Field(
        None, description="When to retry (if generating)"
    )
    link: Optional[str] = Field(None, description="Link to the report (if available)")
    last_updated: Optional[datetime] = Field(
        None, description="When the report was last updated"
    )
    error: Optional[str] = Field(None, description="Error message (if status is error)")


class HealthResponse(BaseModel):
    """Response model for health checks."""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Service version")
    checks: Dict[str, Any] = Field(..., description="Individual health check results")


class CacheMetadata(BaseModel):
    """Metadata for cached analysis results."""

    generated_date: datetime = Field(..., description="When the analysis was generated")
    model: str = Field(..., description="Model used for analysis")
    repo_url: str = Field(..., description="Repository URL that was analyzed")
    format: FormatEnum = Field(..., description="Output format")
    github_token_available: bool = Field(
        ..., description="Whether GitHub token was available"
    )
    repo_owner: str = Field(..., description="Repository owner")
    repo_name: str = Field(..., description="Repository name")


class ConfigResponse(BaseModel):
    """Response model for configuration information."""

    allowed_models: List[str] = Field(..., description="List of allowed LLM models")
    default_model: str = Field(..., description="Default LLM model")


class ModelsResponse(BaseModel):
    """Response model for available models."""

    models: List[str] = Field(..., description="List of available model IDs")
