"""Caching system for analysis results."""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from git_fork_recon.config import Config
from .models import CacheMetadata, FormatEnum


logger = logging.getLogger(__name__)


class CacheManager:
    """Manages cached analysis results with versioned storage."""

    def __init__(self, cache_dir: Optional[Path] = None, config: Optional[Config] = None):
        """Initialize cache manager.

        Args:
            cache_dir: Base directory for cache. If None, uses config.server_cache_dir,
                      config.cache_report, or defaults to platformdirs user cache directory.
            config: Configuration object. If None, falls back to environment variables.
        """
        if cache_dir is None:
            if config and config.server_cache_dir:
                cache_dir = config.server_cache_dir
            elif config:
                cache_dir = config.cache_report
            else:
                from platformdirs import user_cache_dir
                cache_dir = Path(user_cache_dir("git-fork-recon/reports"))

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache initialized at: {self.cache_dir}")

    def get_repo_cache_dir(self, repo_owner: str, repo_name: str) -> Path:
        """Get the cache directory for a specific repository."""
        return self.cache_dir / repo_owner / repo_name

    def get_version_cache_dir(self, repo_owner: str, repo_name: str, timestamp: str) -> Path:
        """Get the cache directory for a specific version."""
        repo_cache = self.get_repo_cache_dir(repo_owner, repo_name)
        version_dir = repo_cache / timestamp
        version_dir.mkdir(parents=True, exist_ok=True)
        return version_dir

    def generate_timestamp(self) -> str:
        """Generate a filesystem-friendly timestamp."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

    def get_latest_version(self, repo_owner: str, repo_name: str) -> Optional[str]:
        """Get the timestamp of the latest cached version."""
        repo_cache = self.get_repo_cache_dir(repo_owner, repo_name)
        latest_link = repo_cache / "latest"

        if latest_link.exists() and latest_link.is_symlink():
            try:
                import os
                return os.readlink(latest_link)
            except OSError:
                pass

        # Fallback: find most recent directory
        if repo_cache.exists():
            versions = [d for d in repo_cache.iterdir() if d.is_dir() and d.name != "latest"]
            if versions:
                return max(versions, key=lambda x: x.name).name

        return None

    def update_latest_symlink(self, repo_owner: str, repo_name: str, timestamp: str) -> None:
        """Update the 'latest' symlink to point to the specified version."""
        repo_cache = self.get_repo_cache_dir(repo_owner, repo_name)
        latest_link = repo_cache / "latest"

        # Remove existing symlink if it exists
        if latest_link.exists():
            latest_link.unlink()

        # Create new symlink
        latest_link.symlink_to(timestamp)

    def _format_to_extension(self, format_value: str) -> str:
        """Convert format value to file extension.

        Args:
            format_value: Format value from FormatEnum

        Returns:
            File extension to use
        """
        if format_value == "markdown":
            return "md"
        return format_value

    def save_result(self, repo_owner: str, repo_name: str, content: str,
                   metadata: CacheMetadata) -> str:
        """Save analysis result to cache.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            content: Report content
            metadata: Cache metadata

        Returns:
            Timestamp of the saved version
        """
        timestamp = self.generate_timestamp()
        version_dir = self.get_version_cache_dir(repo_owner, repo_name, timestamp)

        # Convert format to file extension
        file_extension = self._format_to_extension(metadata.format.value)

        # Save report content
        report_file = version_dir / f"report.{file_extension}"
        report_file.write_text(content)

        # Save metadata
        metadata_file = version_dir / "metadata.json"
        metadata_file.write_text(metadata.model_dump_json(indent=2))

        # Update latest symlink
        self.update_latest_symlink(repo_owner, repo_name, timestamp)

        logger.info(f"Saved analysis result to {version_dir}")
        return timestamp

    def get_result(self, repo_owner: str, repo_name: str,
                   timestamp: Optional[str] = None, requested_format: Optional[str] = None) -> Optional[tuple[str, CacheMetadata]]:
        """Get cached analysis result.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            timestamp: Specific version timestamp. If None, uses latest.
            requested_format: Specific format requested (e.g., 'json', 'html', 'pdf'). If None, uses default from metadata.

        Returns:
            Tuple of (content, metadata) if found, None otherwise
        """
        if timestamp is None:
            timestamp = self.get_latest_version(repo_owner, repo_name)
            if timestamp is None:
                return None

        version_dir = self.get_version_cache_dir(repo_owner, repo_name, timestamp)
        metadata_file = version_dir / "metadata.json"

        if not metadata_file.exists():
            return None

        try:
            # Load metadata
            metadata = CacheMetadata.model_validate_json(metadata_file.read_text())

            # Determine which file to load
            if requested_format and requested_format != metadata.format.value:
                # Requested format is different from source format
                file_extension = requested_format
                report_file = version_dir / f"report.{file_extension}"
                if not report_file.exists():
                    # The converted format doesn't exist
                    return None
            else:
                # Use the original format
                file_extension = self._format_to_extension(metadata.format.value)
                report_file = version_dir / f"report.{file_extension}"
                if not report_file.exists():
                    return None

            content = report_file.read_text()
            return content, metadata

        except Exception as e:
            logger.error(f"Error loading cached result: {e}")
            return None

    def get_metadata(self, repo_owner: str, repo_name: str, timestamp: str) -> Optional[CacheMetadata]:
        """Get metadata for a specific report version."""
        version_dir = self.get_version_cache_dir(repo_owner, repo_name, timestamp)
        metadata_file = version_dir / "metadata.json"

        if not metadata_file.exists():
            return None

        try:
            metadata = CacheMetadata.model_validate_json(metadata_file.read_text())
            return metadata
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return None

    def get_cache_info(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Get information about cached versions."""
        repo_cache = self.get_repo_cache_dir(repo_owner, repo_name)

        if not repo_cache.exists():
            return {"exists": False, "versions": []}

        versions = []
        for version_dir in repo_cache.iterdir():
            if version_dir.is_dir() and version_dir.name != "latest":
                metadata_file = version_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = CacheMetadata.model_validate_json(metadata_file.read_text())
                        versions.append({
                            "timestamp": version_dir.name,
                            "generated_date": metadata.generated_date,
                            "model": metadata.model,
                            "format": metadata.format.value
                        })
                    except Exception:
                        pass

        latest = self.get_latest_version(repo_owner, repo_name)

        return {
            "exists": True,
            "latest": latest,
            "versions": sorted(versions, key=lambda x: x["generated_date"], reverse=True)
        }