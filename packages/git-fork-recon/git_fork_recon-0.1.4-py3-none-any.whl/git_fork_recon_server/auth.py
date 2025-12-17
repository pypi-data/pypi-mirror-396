"""Authentication middleware for the server."""

import logging
from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from git_fork_recon.config import Config


logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for Bearer token authentication."""

    def __init__(self, app, config: Optional[Config] = None, token: Optional[str] = None):
        """Initialize authentication middleware.

        Args:
            app: FastAPI application
            config: Configuration object. If None, falls back to environment variables.
            token: Expected bearer token. If None, reads from config or AUTH_BEARER_TOKEN env var
        """
        super().__init__(app)
        if config:
            self.token = token or config.server_auth_bearer_token
            self.disabled = config.server_disable_auth
        else:
            import os
            self.token = token or os.getenv("AUTH_BEARER_TOKEN")
            self.disabled = os.getenv("DISABLE_AUTH", "0").lower() in ("1", "true", "yes")

        if not self.disabled and not self.token:
            logger.warning("AUTH_BEARER_TOKEN not set and auth not disabled")

    async def dispatch(self, request: Request, call_next):
        """Process request with authentication check."""
        # Skip authentication for health endpoints
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # Skip authentication for UI and static files
        if request.url.path in ("/ui", "/") or request.url.path.startswith("/static/"):
            return await call_next(request)

        # Skip authentication for config and models endpoints (needed by UI)
        if request.url.path in ("/config", "/models"):
            return await call_next(request)

        # Skip authentication if disabled
        if self.disabled:
            return await call_next(request)

        # Allow browser requests to API endpoints (for UI functionality)
        # This enables the UI to work without requiring token management
        # Note: This is intended for local development. For production deployments
        # with authentication enabled, consider implementing token-based auth in the UI
        referer = request.headers.get("referer", "")
        accept = request.headers.get("accept", "")
        is_browser_request = (
            "/ui" in referer or "/static/" in referer or "text/html" in accept
        )

        # Allow browser requests to API endpoints
        if (
            is_browser_request
            and (
                request.url.path.startswith("/analyze")
                or request.url.path.startswith("/report/")
                or request.url.path.startswith("/metadata/")
            )
        ):
            return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract and validate token
        provided_token = auth_header[7:].strip()
        if provided_token != self.token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Token is valid, proceed with request
        return await call_next(request)