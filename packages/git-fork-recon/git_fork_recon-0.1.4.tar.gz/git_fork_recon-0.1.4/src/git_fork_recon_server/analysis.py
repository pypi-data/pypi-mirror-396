"""Background analysis tasks and job management."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Set
import re
from concurrent.futures import ThreadPoolExecutor

from git_fork_recon.main import analyze_forks
from git_fork_recon.config import Config
from .models import AnalysisStatus, AnalysisResponse, FormatEnum
from .cache import CacheManager, CacheMetadata


logger = logging.getLogger(__name__)


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repository name from a GitHub URL."""
    url = url.rstrip("/")
    pattern = r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub repository URL")
    return match.group(1), match.group(2)


class AnalysisManager:
    """Manages background analysis tasks."""

    def __init__(self, cache_manager: CacheManager, config: Config):
        """Initialize analysis manager."""
        self.cache_manager = cache_manager
        self.active_jobs: Dict[str, datetime] = {}
        self.max_concurrent = config.server_parallel_tasks
        self.allowed_models = set(config.server_allowed_models) if config.server_allowed_models else set()
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent)
        logger.info(f"Analysis manager initialized with {self.max_concurrent} concurrent tasks")

    def _get_job_key(self, repo_url: str, model: Optional[str]) -> str:
        """Generate a unique key for an analysis job."""
        model_part = model or "default"
        return f"{repo_url}::{model_part}"

    def _validate_model(self, model: Optional[str]) -> None:
        """Validate that the model is allowed."""
        if not model:
            return

        if not self.allowed_models:
            logger.warning("No ALLOWED_MODELS configured, allowing any model")
            return

        if model not in self.allowed_models:
            raise ValueError(f"Model '{model}' is not in the allowed models list")

    def can_start_analysis(self, repo_url: str, model: Optional[str]) -> bool:
        """Check if we can start a new analysis."""
        if len(self.active_jobs) >= self.max_concurrent:
            return False

        job_key = self._get_job_key(repo_url, model)
        return job_key not in self.active_jobs

    def start_analysis(self, repo_url: str, model: Optional[str]) -> None:
        """Start tracking an analysis job."""
        job_key = self._get_job_key(repo_url, model)
        self.active_jobs[job_key] = datetime.now(timezone.utc)
        logger.info(f"Started analysis job: {job_key}")

    def finish_analysis(self, repo_url: str, model: Optional[str]) -> None:
        """Finish tracking an analysis job."""
        job_key = self._get_job_key(repo_url, model)
        if job_key in self.active_jobs:
            del self.active_jobs[job_key]
            logger.info(f"Finished analysis job: {job_key}")

    def get_job_count(self) -> int:
        """Get current number of active jobs."""
        return len(self.active_jobs)

    def get_retry_after(self) -> datetime:
        """Calculate when the next job might be available."""
        if len(self.active_jobs) < self.max_concurrent:
            return datetime.now(timezone.utc)

        # Estimate 5 minutes per job as a rough estimate
        oldest_job = min(self.active_jobs.values())
        return oldest_job + timedelta(minutes=5)

    async def analyze_repository(
        self,
        repo_url: str,
        model: Optional[str] = None,
        github_token: Optional[str] = None,
        format: FormatEnum = FormatEnum.markdown,
        nocache: bool = False,
    ) -> AnalysisResponse:
        """Analyze a repository with caching support."""
        try:
            # Validate model
            self._validate_model(model)

            # Parse repository URL
            owner, repo_name = parse_github_url(str(repo_url))

            # Check cache first if not forcing re-analysis
            if not nocache:
                cached_result = self.cache_manager.get_result(owner, repo_name, requested_format=format.value)
                if cached_result:
                    content, metadata = cached_result
                    return AnalysisResponse(
                        status=AnalysisStatus.available,
                        link=f"/report/{owner}/{repo_name}/latest/report.{self._format_to_extension(format.value)}",
                        last_updated=metadata.generated_date,
                    )

            # Check if we can start a new analysis
            if not self.can_start_analysis(str(repo_url), model):
                retry_after = self.get_retry_after()
                return AnalysisResponse(
                    status=AnalysisStatus.generating,
                    retry_after=retry_after,
                )

            # Return "generating" status - the actual analysis will be done by background task
            self.start_analysis(str(repo_url), model)
            return AnalysisResponse(
                status=AnalysisStatus.generating,
            )

        except Exception as e:
            logger.error(f"Error analyzing repository {repo_url}: {e}")
            return AnalysisResponse(
                status=AnalysisStatus.error,
                error=str(e),
            )

    def _format_to_extension(self, format_value: str) -> str:
        """Convert format value to file extension."""
        if format_value == "markdown":
            return "md"
        return format_value

    async def run_analysis_task(
        self,
        repo_url: str,
        model: Optional[str] = None,
        github_token: Optional[str] = None,
        format: FormatEnum = FormatEnum.markdown,
    ) -> None:
        """Run an analysis task in the background."""
        try:
            # Parse repository URL
            owner, repo_name = parse_github_url(repo_url)

            # Perform analysis in a thread pool to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                self.executor,
                analyze_forks,
                str(repo_url),
                None,  # env_file
                model,
                None,  # context_length
                None,  # api_base_url
                None,  # api_key_env_var
                5,  # parallel
                False,  # clear_cache
                None,  # activity_threshold
                None,  # max_forks
                github_token,
            )

            # Save to cache
            metadata = CacheMetadata(
                generated_date=result.generated_at,
                model=model or result.config.model,
                repo_url=str(repo_url),
                format=format,
                github_token_available=bool(github_token or result.config.github_token),
                repo_owner=owner,
                repo_name=repo_name,
            )

            self.cache_manager.save_result(owner, repo_name, result.report, metadata)

            logger.info(f"Background analysis completed for {repo_url}")

        except Exception as e:
            logger.error(f"Background analysis task failed for {repo_url}: {e}")
        finally:
            # Make sure to finish tracking the job
            self.finish_analysis(repo_url, model)