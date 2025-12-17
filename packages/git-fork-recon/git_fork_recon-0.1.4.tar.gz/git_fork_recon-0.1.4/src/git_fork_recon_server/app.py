"""FastAPI application for git-fork-recon server."""

import logging
import os
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

import httpx

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import AnalysisRequest, AnalysisResponse, HealthResponse, ConfigResponse, ModelsResponse
from .cache import CacheManager
from .analysis import AnalysisManager
from .auth import AuthMiddleware
from git_fork_recon.config import load_config


logger = logging.getLogger(__name__)


def _format_to_extension(format_value: str) -> str:
    """Convert format value to file extension."""
    if format_value == "markdown":
        return "md"
    return format_value


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise
    
    app = FastAPI(
        title="Git Fork Recon Server",
        description="REST API for analyzing GitHub repository fork networks",
        version="0.1.0",
    )

    # Initialize components with config
    cache_manager = CacheManager(config=config)
    analysis_manager = AnalysisManager(cache_manager, config=config)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add authentication middleware
    app.add_middleware(AuthMiddleware, config=config)

    @app.get("/health")
    async def health_check() -> HealthResponse:
        """Basic health check endpoint."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version="0.1.0",
            checks={
                "cache": {"status": "ok", "path": str(cache_manager.cache_dir)},
                "auth": {"disabled": config.server_disable_auth},
                "concurrent_jobs": analysis_manager.get_job_count(),
                "max_concurrent": analysis_manager.max_concurrent,
            },
        )

    @app.get("/health/ready")
    async def readiness_check() -> HealthResponse:
        """Readiness check endpoint."""
        # Check if we can accept new jobs
        can_accept = analysis_manager.get_job_count() < analysis_manager.max_concurrent

        return HealthResponse(
            status="ready" if can_accept else "busy",
            timestamp=datetime.now(timezone.utc),
            version="0.1.0",
            checks={
                "cache": {"status": "ok", "path": str(cache_manager.cache_dir)},
                "auth": {"disabled": config.server_disable_auth},
                "concurrent_jobs": analysis_manager.get_job_count(),
                "max_concurrent": analysis_manager.max_concurrent,
                "can_accept_new_jobs": can_accept,
            },
        )

    @app.get("/config", response_model=ConfigResponse)
    async def get_config() -> ConfigResponse:
        """Get server configuration information."""
        return ConfigResponse(
            allowed_models=(
                list(analysis_manager.allowed_models)
                if analysis_manager.allowed_models
                else []
            ),
            default_model=config.model,
        )

    @app.get("/models", response_model=ModelsResponse)
    async def get_models() -> ModelsResponse:
        """Get available models from the LLM API."""
        try:
            config = load_config()
            base_url = config.openai_base_url
            api_key = config.openai_api_key
            
            # Ensure base_url ends with a slash
            if not base_url.endswith("/"):
                base_url += "/"
            
            models_url = f"{base_url}models"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/git-fork-recon",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(models_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Extract model IDs from the response
                models = [model["id"] for model in data.get("data", [])]
                return ModelsResponse(models=models)
        except Exception as e:
            logger.error(f"Error fetching models from API: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch models from API: {str(e)}"
            )

    @app.post("/analyze", response_model=AnalysisResponse)
    async def analyze_repository(
        request: AnalysisRequest,
        background_tasks: BackgroundTasks,
    ) -> AnalysisResponse:
        """Start repository analysis."""
        # Convert to dict and remove None values
        kwargs = {
            "repo_url": str(request.repo_url),
            "model": request.model,
            "github_token": request.github_token,
            "format": request.format,
            "nocache": request.nocache,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Get analysis response
        response = await analysis_manager.analyze_repository(**kwargs)

        # If analysis needs to be started, add background task
        if response.status == "generating":
            task_kwargs = {
                "repo_url": str(request.repo_url),
                "model": request.model,
                "github_token": request.github_token,
                "format": request.format,
            }
            task_kwargs = {k: v for k, v in task_kwargs.items() if v is not None}

            background_tasks.add_task(analysis_manager.run_analysis_task, **task_kwargs)

        return response

    @app.get("/report/{owner}/{repo}/{timestamp}/report.{format}")
    async def get_report(
        owner: str,
        repo: str,
        timestamp: str,
        format: str,
    ):
        """Get a cached report."""
        # Map URL format to API format
        url_to_api_format = {
            "md": "markdown",
            "markdown": "markdown",  # for backward compatibility
            "json": "json",
            "html": "html",
            "pdf": "pdf",
        }

        api_format = url_to_api_format.get(format)
        if api_format is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Allowed: {list(url_to_api_format.keys())}",
            )

        # Get cached result
        result = cache_manager.get_result(
            owner, repo, timestamp, requested_format=api_format
        )
        if not result:
            raise HTTPException(status_code=404, detail="Report not found")

        content, metadata = result

        # Return content directly
        return Response(
            content=content,
            media_type=_get_media_type(api_format),
            headers={
                "Content-Disposition": f"attachment; filename={owner}-{repo}-forks.{format}"
            },
        )

    @app.get("/report/{owner}/{repo}/latest/report.{format}")
    async def get_latest_report(
        owner: str,
        repo: str,
        format: str,
    ):
        """Get the latest cached report."""
        # Map URL format to API format
        url_to_api_format = {
            "md": "markdown",
            "markdown": "markdown",  # for backward compatibility
            "json": "json",
            "html": "html",
            "pdf": "pdf",
        }

        api_format = url_to_api_format.get(format)
        if api_format is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Allowed: {list(url_to_api_format.keys())}",
            )

        # Get latest version
        latest = cache_manager.get_latest_version(owner, repo)
        if not latest:
            raise HTTPException(
                status_code=404, detail="No reports found for this repository"
            )

        # Get cached result
        result = cache_manager.get_result(
            owner, repo, latest, requested_format=api_format
        )
        if not result:
            raise HTTPException(status_code=404, detail="Report not found")

        content, metadata = result

        # Return content directly
        return Response(
            content=content,
            media_type=_get_media_type(api_format),
            headers={
                "Content-Disposition": f"attachment; filename={owner}-{repo}-forks.{format}"
            },
        )

    @app.get("/metadata/{owner}/{repo}/{timestamp}")
    async def get_metadata(
        owner: str,
        repo: str,
        timestamp: str,
    ):
        """Get metadata for a specific report version."""
        metadata = cache_manager.get_metadata(owner, repo, timestamp)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")

        return metadata

    @app.get("/metadata/{owner}/{repo}/latest")
    async def get_latest_metadata(
        owner: str,
        repo: str,
    ):
        """Get metadata for the latest report."""
        latest = cache_manager.get_latest_version(owner, repo)
        if not latest:
            raise HTTPException(
                status_code=404, detail="No reports found for this repository"
            )

        metadata = cache_manager.get_metadata(owner, repo, latest)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")

        return metadata

    @app.get("/report/{owner}/{repo}/{timestamp}/status")
    async def get_report_status(
        owner: str,
        repo: str,
        timestamp: str,
    ):
        """Get status for a specific report version."""
        # Check if this analysis is currently running for any model
        repo_url = f"https://github.com/{owner}/{repo}"

        # Check if there are any active jobs for this repository (regardless of model)
        active_repo_jobs = [
            key
            for key in analysis_manager.active_jobs.keys()
            if key.startswith(f"{repo_url}::")
        ]
        if active_repo_jobs:
            retry_after = analysis_manager.get_retry_after()
            return {
                "status": "generating",
                "retry-after": retry_after.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            }

        # Check if the specific version exists
        metadata = cache_manager.get_metadata(owner, repo, timestamp)
        if metadata:
            return {
                "status": "available",
                "link": f"/report/{owner}/{repo}/{timestamp}/report.{_format_to_extension(metadata.format.value)}",
                "generated_date": metadata.generated_date.isoformat(),
                "model": metadata.model,
            }
        else:
            return {"status": "not_found"}

    @app.get("/report/{owner}/{repo}/latest/status")
    async def get_latest_report_status(
        owner: str,
        repo: str,
    ):
        """Get status for the latest report."""
        # Check if this analysis is currently running for any model
        repo_url = f"https://github.com/{owner}/{repo}"

        # Check if there are any active jobs for this repository (regardless of model)
        active_repo_jobs = [
            key
            for key in analysis_manager.active_jobs.keys()
            if key.startswith(f"{repo_url}::")
        ]
        if active_repo_jobs:
            retry_after = analysis_manager.get_retry_after()
            return {
                "status": "generating",
                "retry-after": retry_after.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            }

        # Check if any version exists
        latest = cache_manager.get_latest_version(owner, repo)
        if not latest:
            return {"status": "not_found"}

        metadata = cache_manager.get_metadata(owner, repo, latest)
        if metadata:
            return {
                "status": "available",
                "link": f"/report/{owner}/{repo}/latest/report.{_format_to_extension(metadata.format.value)}",
                "generated_date": metadata.generated_date.isoformat(),
                "model": metadata.model,
            }
        else:
            return {"status": "not_found"}

    def _get_media_type(format: str) -> str:
        """Get the appropriate media type for a format."""
        media_types = {
            "markdown": "text/markdown",
            "json": "application/json",
            "html": "text/html",
            "pdf": "application/pdf",
        }
        return media_types.get(format, "text/plain")

    # Mount static files and add UI endpoint if not disabled
    if not config.server_disable_ui:
        # Mount static files
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")

        @app.get("/favicon.ico")
        async def favicon():
            """Serve the favicon."""
            favicon_path = os.path.join(static_dir, "favicon.ico")
            if os.path.exists(favicon_path):
                return FileResponse(favicon_path)
            raise HTTPException(status_code=404, detail="Favicon not found")

        @app.get("/ui")
        async def serve_ui():
            """Serve the web UI."""
            return FileResponse(os.path.join(static_dir, "index.html"))

        # Add redirect for GET / to /ui (unless it's an API request)
        @app.get("/")
        async def root_redirect(request: Request):
            """Redirect root to UI for browser requests."""
            # Check if the request accepts HTML (browser request)
            accept_header = request.headers.get("accept", "")
            if "text/html" in accept_header or "*/*" in accept_header:
                from fastapi.responses import RedirectResponse

                return RedirectResponse(url="/ui", status_code=302)

            # For API requests, return JSON response
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Git Fork Recon Server",
                    "version": "0.1.0",
                    "endpoints": {
                        "analyze": "/analyze",
                        "config": "/config",
                        "reports": "/report/{owner}/{repo}/{timestamp}/report.{format}",
                        "latest_report": "/report/{owner}/{repo}/latest/report.{format}",
                        "health": "/health",
                        "ready": "/health/ready",
                        "ui": "/ui",
                    },
                },
            )

    return app
