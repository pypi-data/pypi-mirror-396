#!/usr/bin/env python

"""CLI for the git-fork-recon server."""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from .app import create_app
from git_fork_recon.config import load_config

app = typer.Typer()
console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@app.command()
def main(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Host to bind the server to",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        help="Port to bind the server to",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload for development",
    ),
    log_level: str = typer.Option(
        "info",
        "--log-level",
        help="Log level (debug, info, warning, error)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
) -> None:
    """Start the git-fork-recon server."""
    # Set up logging
    setup_logging(verbose)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise typer.Exit(1)

    # Override host/port from command line if different from defaults
    effective_host = host if host != "127.0.0.1" else config.server_host
    effective_port = port if port != 8000 else config.server_port

    # Import uvicorn and start the server
    try:
        import uvicorn
    except ImportError:
        console.print("[red]Error: uvicorn is required to run the server[/red]")
        console.print("Install it with: pip install 'git-fork-recon[server]'")
        raise typer.Exit(1)

    # Show startup information
    console.print(f"[green]Starting Git Fork Recon server[/green]")
    console.print(f"Host: {effective_host}")
    console.print(f"Port: {effective_port}")
    console.print(f"Reload: {'Yes' if reload else 'No'}")
    console.print(f"Log level: {log_level}")

    if config.server_disable_auth:
        console.print("[yellow]Authentication is disabled[/yellow]")
    else:
        console.print("Authentication is enabled")

    if config.server_allowed_models:
        console.print(f"Allowed models: {', '.join(config.server_allowed_models)}")

    cache_dir = config.server_cache_dir or config.cache_report
    console.print(f"Cache directory: {cache_dir}")
    console.print(f"Max parallel tasks: {config.server_parallel_tasks}")
    console.print("")

    # Start the server
    uvicorn.run(
        "git_fork_recon_server.app:create_app",
        host=effective_host,
        port=effective_port,
        reload=reload,
        log_level=log_level,
        factory=True,
    )


if __name__ == "__main__":
    app()