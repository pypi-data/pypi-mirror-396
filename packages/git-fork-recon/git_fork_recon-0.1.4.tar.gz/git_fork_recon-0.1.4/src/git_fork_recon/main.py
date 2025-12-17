#!/usr/bin/env python

from typing import Optional, Dict, Any
import logging
from pathlib import Path
from datetime import datetime, timezone
import os
import sys
import shutil

from .config import load_config
from .github.api import GithubClient
from .git.repo import GitRepo
from .llm.client import LLMClient
from .report.generator import ReportGenerator


logger = logging.getLogger(__name__)


class AnalysisResult:
    """Container for analysis results."""

    def __init__(self, repo_info: Any, forks: list, git_repo: Any, report: str, config: Any):
        self.repo_info = repo_info
        self.forks = forks
        self.git_repo = git_repo
        self.report = report
        self.config = config
        self.generated_at = datetime.now(timezone.utc)


def analyze_forks(
    repo_url: str,
    config_file: Optional[Path] = None,
    model: Optional[str] = None,
    context_length: Optional[int] = None,
    api_base_url: Optional[str] = None,
    api_key_env_var: Optional[str] = None,
    parallel: int = 5,
    clear_cache: bool = False,
    activity_threshold: Optional[datetime] = None,
    max_forks: Optional[int] = None,
    github_token: Optional[str] = None,
) -> AnalysisResult:
    """Analyze forks of a GitHub repository and return results."""
    # Load config and apply overrides
    config = load_config(config_file, api_key_env_var=api_key_env_var)

    # Override config with command line options if provided
    if model is not None:
        config.model = model
    if context_length is not None:
        config.context_length = context_length
    if api_base_url is not None:
        config.openai_base_url = api_base_url
    if github_token is not None:
        config.github_token = github_token

    # Initialize clients with parallel option
    github_client = GithubClient(config.github_token, max_parallel=parallel)
    llm_client = LLMClient(
        config.openai_api_key,
        model=config.model,
        context_length=config.context_length,
        api_base_url=config.openai_base_url,
        max_parallel=parallel,
    )

    # Get repository and fork information
    repo_info = github_client.get_repository(repo_url)

    # Clear cache only if requested
    if clear_cache and config.cache_repo:
        repo_cache = config.cache_repo / repo_info.owner / repo_info.name
        if repo_cache.exists():
            logger.info(f"Clearing cache for {repo_cache}")
            shutil.rmtree(repo_cache)

    # Clone main repository
    git_repo = GitRepo(repo_info, config)

    # Get and filter forks
    forks = github_client.get_forks(repo_info, max_forks=max_forks)

    # Apply activity threshold if specified
    if activity_threshold:
        active_forks = [
            fork
            for fork in forks
            if datetime.fromisoformat(fork.last_updated) >= activity_threshold
        ]
        logger.info(
            f"Found {len(active_forks)} forks active since {activity_threshold} out of {len(forks)} processed forks"
        )
        forks_to_analyze = active_forks
    else:
        forks_to_analyze = forks

    # Generate report
    report_gen = ReportGenerator(llm_client)
    report = report_gen.generate(repo_info, forks_to_analyze, git_repo)

    return AnalysisResult(repo_info, forks_to_analyze, git_repo, report, config)


def analyze(
    repo_url: str,
    output: Optional[Path] = None,
    output_formats: Optional[str] = None,
    active_within: Optional[str] = None,
    config_file: Optional[Path] = None,
    model: Optional[str] = None,
    context_length: Optional[int] = None,
    api_base_url: Optional[str] = None,
    api_key_env_var: Optional[str] = None,
    parallel: int = 5,
    verbose: bool = False,
    clear_cache: bool = False,
    activity_threshold: Optional[datetime] = None,
    max_forks: Optional[int] = None,
) -> None:
    """Analyze forks of a GitHub repository (CLI interface)."""
    # Load config and apply overrides
    config = load_config(config_file, api_key_env_var=api_key_env_var)

    # Override config with command line options if provided
    if model is not None:
        config.model = model
    if context_length is not None:
        config.context_length = context_length
    if api_base_url is not None:
        config.openai_base_url = api_base_url

    # Log final configuration
    logger.info(f"Found GITHUB_TOKEN: {'yes' if config.github_token else 'no'}")
    logger.info(f"Using API key from: {config.api_key_source}")
    logger.info(f"Found API key: {'yes' if config.openai_api_key else 'no'}")
    logger.info(f"Using API base URL: {config.openai_base_url}")
    logger.info(f"Using CACHE_REPO: {config.cache_repo}")
    logger.info(f"Using MODEL: {config.model}")
    if config.context_length is not None:
        logger.info(f"Using CONTEXT_LENGTH override: {config.context_length}")
    logger.info(f"Maximum forks to analyze: {max_forks}")

    # Perform analysis
    result = analyze_forks(
        repo_url=repo_url,
        config_file=config_file,
        model=model,
        context_length=context_length,
        api_base_url=api_base_url,
        api_key_env_var=api_key_env_var,
        parallel=parallel,
        clear_cache=clear_cache,
        activity_threshold=activity_threshold,
        max_forks=max_forks,
    )

    # Write report to file or stdout
    if output is None or str(output) == "-":
        sys.stdout.write(result.report)
    else:
        output.write_text(result.report)
        logger.info(f"Report written to {output}")

        # Handle additional output formats if specified
        if output_formats:
            from .llm.client import LLMClient
            llm_client = LLMClient(
                result.config.openai_api_key,
                model=result.config.model,
                context_length=result.config.context_length,
                api_base_url=result.config.openai_base_url,
                max_parallel=parallel,
            )
            report_gen = ReportGenerator(llm_client)
            report_gen.convert_report(output, output_formats.split(","))
