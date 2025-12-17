from pathlib import Path
from typing import Optional, Dict, Any
import sys
import os
import re
import logging
import webbrowser

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python <3.11

from pydantic import BaseModel, Field
from platformdirs import user_config_dir, user_cache_dir
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

logger = logging.getLogger(__name__)
console = Console()


class Config(BaseModel):
    github_token: str = Field(..., description="GitHub API token")
    openai_api_key: str = Field(..., description="OpenAI-compatible API key")
    api_key_source: str = Field(
        ..., description="Environment variable that provided the API key"
    )
    openai_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenAI-compatible API base URL",
    )
    cache_repo: Path = Field(
        default=Path(user_cache_dir("git-fork-recon/repos")),
        description="Directory for caching repository data",
    )
    cache_report: Path = Field(
        default=Path(user_cache_dir("git-fork-recon/reports")),
        description="Directory for caching report data",
    )
    model: str = Field(
        default="deepseek/deepseek-chat-v3-0324:free",
        description="Model to use",
    )
    context_length: Optional[int] = Field(
        default=None,
        description="Override model context length (if not set, uses API value)",
    )
    # Server configuration
    server_allowed_models: Optional[list[str]] = Field(
        default=None,
        description="List of allowed LLM models for server (None = unrestricted)",
    )
    server_parallel_tasks: int = Field(
        default=2,
        description="Maximum concurrent analysis tasks",
    )
    server_disable_auth: bool = Field(
        default=True,
        description="Disable authentication for server",
    )
    server_auth_bearer_token: Optional[str] = Field(
        default=None,
        description="Bearer token for server authentication",
    )
    server_cache_dir: Optional[Path] = Field(
        default=None,
        description="Server cache directory (None = use cache_report)",
    )
    server_disable_ui: bool = Field(
        default=False,
        description="Disable web UI",
    )
    server_host: str = Field(
        default="127.0.0.1",
        description="Server host",
    )
    server_port: int = Field(
        default=8000,
        description="Server port",
    )


def _is_pure_env_var_reference(value: str) -> bool:
    """Check if a string is a pure environment variable reference.
    
    A pure env var reference is of the form $VAR_NAME where VAR_NAME
    is a valid environment variable name (alphanumeric + underscore, starting with letter/underscore).
    """
    if not isinstance(value, str) or not value.startswith("$"):
        return False
    # Match pattern: $ followed by valid env var name (no path separators or other special chars)
    pattern = r"^\$[A-Za-z_][A-Za-z0-9_]*$"
    return bool(re.match(pattern, value))


def _resolve_env_var(value: str) -> str:
    """Resolve environment variable references in config values.
    
    If value is a pure env var reference (e.g., $VAR_NAME), resolve it and raise error if not set.
    For paths with $HOME, use _expand_path() instead.
    """
    if _is_pure_env_var_reference(value):
        env_var_name = value[1:]
        env_value = os.getenv(env_var_name)
        if env_value is None:
            raise ValueError(
                f"Environment variable {env_var_name} referenced in config but not set"
            )
        return env_value
    return value


def _expand_path(path: str) -> str:
    """Expand ~ and environment variables in paths using os.path functions."""
    # First expand ~
    path = os.path.expanduser(path)
    # Then expand environment variables (handles $HOME, ${VAR}, etc.)
    path = os.path.expandvars(path)
    return path


def _redact_secret(value: str, show_chars: int = 4) -> str:
    """Partially redact a secret value for display."""
    if not value or len(value) <= show_chars:
        return "****"
    return value[:show_chars] + "****"


def _get_config_path(config_file: Optional[Path] = None) -> Path:
    """Get the path to the config file."""
    if config_file:
        return config_file
    config_dir = Path(user_config_dir("git-fork-recon"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def setup_config_interactive() -> Dict[str, Any]:
    """Interactive setup wizard for first-time configuration."""
    rprint(Panel.fit("[bold cyan]Git Fork Recon Configuration Setup[/bold cyan]"))
    rprint("")
    
    config = {}
    
    # OPENAI_BASE_URL
    rprint(Panel.fit("[bold]OpenAI-Compatible Endpoint Configuration[/bold]"))
    openai_base_url_env = os.getenv("OPENAI_BASE_URL")
    
    options = []
    if openai_base_url_env:
        options.append(("1", openai_base_url_env, f"Current OPENAI_BASE_URL ({openai_base_url_env})"))
    options.extend([
        ("2" if openai_base_url_env else "1", "$OPENAI_BASE_URL", "Always use $OPENAI_BASE_URL"),
        ("3" if openai_base_url_env else "2", "http://localhost:11434/v1", "Local Ollama server (http://localhost:11434/v1)"),
        ("4" if openai_base_url_env else "3", "https://text.pollinations.ai/openai", "Pollinations free API (https://text.pollinations.ai/openai)"),
        ("5" if openai_base_url_env else "4", "https://openrouter.ai/api/v1", "OpenRouter (https://openrouter.ai/api/v1)"),
        ("6" if openai_base_url_env else "5", None, "Enter custom URL"),
    ])
    
    for num, _, desc in options:
        rprint(f"  {num}. {desc}")
    
    default_choice = "1" if openai_base_url_env else "4"
    choice = Prompt.ask("\nSelect endpoint", default=default_choice)
    
    # Find selected option
    selected_value = None
    for num, value, _ in options:
        if choice == num:
            if value is None:  # Custom URL
                selected_value = Prompt.ask("Enter custom endpoint URL")
            else:
                selected_value = value
            break
    
    if not selected_value:
        # Default fallback
        selected_value = openai_base_url_env or "https://openrouter.ai/api/v1"
    
    config["base_url"] = selected_value
    
    selected_base_url = _resolve_env_var(config["base_url"]) if config["base_url"].startswith("$") else config["base_url"]
    
    # OPENAI_API_KEY
    rprint("")
    openai_key_env = os.getenv("OPENAI_API_KEY")
    openrouter_key_env = os.getenv("OPENROUTER_API_KEY")
    api_key_env = openai_key_env or openrouter_key_env
    
    # Check if Ollama is selected
    is_ollama = "ollama" in selected_base_url.lower() or "localhost:11434" in selected_base_url
    
    if is_ollama:
        # Ollama always uses 'ollama' as the default key
        config["api_key"] = "ollama"
        config["api_key_source"] = "manual"
        rprint("Using default Ollama API key: 'ollama'")
    elif api_key_env:
        redacted = _redact_secret(api_key_env)
        env_var_name = "OPENROUTER_API_KEY" if (openrouter_key_env and "openrouter" in selected_base_url.lower()) else "OPENAI_API_KEY"
        rprint(f"Found API key in environment: {redacted}")
        use_env = Confirm.ask(f"Always use the ${env_var_name} environment variable?", default=True)
        if use_env:
            if openrouter_key_env and "openrouter" in selected_base_url.lower():
                config["api_key"] = "$OPENROUTER_API_KEY"
                config["api_key_source"] = "OPENROUTER_API_KEY"
            else:
                config["api_key"] = "$OPENAI_API_KEY"
                config["api_key_source"] = "OPENAI_API_KEY"
        else:
            if "openrouter" in selected_base_url.lower():
                open_browser = Confirm.ask("Open browser to create OpenRouter API key?", default=False)
                if open_browser:
                    webbrowser.open("https://openrouter.ai/settings/keys")
            config["api_key"] = Prompt.ask("Enter API key", password=True)
            config["api_key_source"] = "manual"
    elif "pollinations" in selected_base_url.lower():
        rprint("Pollinations detected - API key can be blank")
        config["api_key"] = Prompt.ask("Enter API key (or leave blank)", default="")
        config["api_key_source"] = "manual"
    elif "openrouter" in selected_base_url.lower():
        open_browser = Confirm.ask("Open browser to create OpenRouter API key?", default=False)
        if open_browser:
            webbrowser.open("https://openrouter.ai/settings/keys")
        config["api_key"] = Prompt.ask("Enter API key", password=True)
        config["api_key_source"] = "manual"
    else:
        use_env = Confirm.ask("Always use the $OPENAI_API_KEY environment variable?", default=False)
        if use_env:
            config["api_key"] = "$OPENAI_API_KEY"
            config["api_key_source"] = "OPENAI_API_KEY"
        else:
            config["api_key"] = Prompt.ask("Enter API key", password=True)
            config["api_key_source"] = "manual"
    
    # MODEL
    rprint("")
    rprint(Panel.fit("[bold]Model Configuration[/bold]"))
    
    if "openrouter" in selected_base_url.lower():
        model_options = [
            "1. z-ai/glm-4.5-air:free",
            "2. openai/gpt-oss-20b:free",
            "3. nvidia/nemotron-nano-12b-v2-vl:free",
            "4. qwen/qwen3-4b:free",
            "5. amazon/nova-2-lite-v1:free",
            "6. Enter custom model",
        ]
        for option in model_options:
            rprint(f"  {option}")
        model_choice = Prompt.ask("Select model", default="1")
        if model_choice == "1":
            config["model"] = "z-ai/glm-4.5-air:free"
        elif model_choice == "2":
            config["model"] = "openai/gpt-oss-20b:free"
        elif model_choice == "3":
            config["model"] = "nvidia/nemotron-nano-12b-v2-vl:free"
        elif model_choice == "4":
            config["model"] = "qwen/qwen3-4b:free"
        elif model_choice == "5":
            config["model"] = "amazon/nova-2-lite-v1:free"
        else:
            config["model"] = Prompt.ask("Enter model name")
    elif "pollinations" in selected_base_url.lower():
        config["model"] = Prompt.ask("Enter model name", default="openai")
    elif "ollama" in selected_base_url.lower() or "localhost:11434" in selected_base_url:
        model_options = [
            "1. qwen3:4b",
            "2. granite4:3b",
            "3. gpt-oss:20b",
            "4. gemma3:4b",
            "5. Enter custom model",
        ]
        for option in model_options:
            rprint(f"  {option}")
        model_choice = Prompt.ask("Select model", default="1")
        if model_choice == "1":
            config["model"] = "qwen3:4b"
        elif model_choice == "2":
            config["model"] = "granite4:3b"
        elif model_choice == "3":
            config["model"] = "gpt-oss:20b"
        elif model_choice == "4":
            config["model"] = "gemma3:4b"
        else:
            config["model"] = Prompt.ask("Enter model name")
    else:
        config["model"] = Prompt.ask("Enter model name")
    
    # GITHUB_TOKEN
    rprint("")
    rprint(Panel.fit("[bold]GitHub Configuration[/bold]"))
    github_token_env = os.getenv("GITHUB_TOKEN")
    if github_token_env:
        redacted = _redact_secret(github_token_env)
        rprint(f"Found GitHub token in environment: {redacted}")
        use_env = Confirm.ask("Always use the $GITHUB_TOKEN environment variable?", default=True)
        if use_env:
            config["github_token"] = "$GITHUB_TOKEN"
        else:
            config["github_token"] = Prompt.ask("Enter GitHub token", password=True)
    else:
        use_env = Confirm.ask("Always use the $GITHUB_TOKEN environment variable?", default=False)
        if use_env:
            config["github_token"] = "$GITHUB_TOKEN"
        else:
            config["github_token"] = Prompt.ask("Enter GitHub token", password=True)
    
    # Cache paths
    rprint("")
    rprint(Panel.fit("[bold]Cache Configuration[/bold]"))
    default_repo_cache = "$HOME/.cache/git-fork-recon/repos"
    default_report_cache = "$HOME/.cache/git-fork-recon/reports"
    
    repo_cache = Prompt.ask("Repository cache directory", default=default_repo_cache)
    report_cache = Prompt.ask("Report cache directory", default=default_report_cache)
    
    config["cache_repo"] = repo_cache
    config["cache_report"] = report_cache
    
    return config


def _escape_toml_string(value: str) -> str:
    """Escape a string for TOML."""
    # Simple escaping - wrap in quotes and escape quotes
    if '"' in value or '\n' in value or '\\' in value:
        # Use triple quotes for complex strings
        return '"""' + value.replace('"""', '\\"""') + '"""'
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _save_config(config: Dict[str, Any], config_path: Path) -> None:
    """Save configuration to TOML file."""
    base_url = config.get('base_url', 'https://openrouter.ai/api/v1')
    api_key = config.get('api_key', '')
    model = config.get('model', 'deepseek/deepseek-chat-v3-0324:free')
    github_token = config.get('github_token', '')
    cache_repo = config.get('cache_repo', '$HOME/.cache/git-fork-recon/repos')
    cache_report = config.get('cache_report', '$HOME/.cache/git-fork-recon/reports')
    
    toml_content = f"""# Configure an OpenAI-compatible endpoint
[endpoint]
base_url = {_escape_toml_string(base_url)}
api_key = {_escape_toml_string(api_key)}
model = {_escape_toml_string(model)}
"""
    
    if config.get('context_length'):
        toml_content += f"context_length = {config['context_length']}\n"
    else:
        toml_content += "# context_length = 64000  # Optional: Override default context length\n"
    
    toml_content += f"""
[github]
token = {_escape_toml_string(github_token)}

[cache]
# Supports $HOME and ~ expansion
repo = {_escape_toml_string(cache_repo)}
report = {_escape_toml_string(cache_report)}

# =============================================================================
# Server Configuration (for git-fork-recon-server)
# =============================================================================
[server]
# Comma-separated list of allowed LLM models (default: unrestricted)
# allowed_models = "deepseek/deepseek-chat-v3.1-terminus,z-ai/glm-4.5-air"

# Server host and port configuration
host = "127.0.0.1"
port = 8000

# Authentication settings
disable_auth = true
# auth_bearer_token = "your-secret-token-here"  # Or use: "$AUTH_BEARER_TOKEN"

# Maximum concurrent analysis tasks (default: 2)
parallel_tasks = 2

# Server cache directory (default: uses cache.report)
# cache_dir = "$HOME/.cache/git-fork-recon/reports"

# Web UI settings
disable_ui = false  # Set to true to disable the web UI at /ui endpoint
"""
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(toml_content)


def load_config(
    config_file: Optional[Path] = None,
    api_key_env_var: Optional[str] = None,
) -> Config:
    """Load configuration from TOML file."""
    config_path = _get_config_path(config_file)
    
    # If config doesn't exist, run interactive setup
    if not config_path.exists():
        logger.info("Config file not found. Starting interactive setup...")
        config_dict = setup_config_interactive()
        _save_config(config_dict, config_path)
        rprint(f"\n[green]✓[/green] Configuration saved to: {config_path}")
        rprint("")
    
    # Load TOML file
    with open(config_path, "rb") as f:
        toml_data = tomllib.load(f)
    
    # Extract endpoint config
    endpoint = toml_data.get("endpoint", {})
    github = toml_data.get("github", {})
    cache = toml_data.get("cache", {})
    server = toml_data.get("server", {})
    
    # Resolve environment variable references
    openai_base_url = _resolve_env_var(endpoint.get("base_url", "https://openrouter.ai/api/v1"))
    openai_api_key = _resolve_env_var(endpoint.get("api_key", ""))
    github_token = _resolve_env_var(github.get("token", ""))
    
    # Handle API key source
    api_key_source = "manual"
    if endpoint.get("api_key", "").startswith("$"):
        api_key_source = endpoint["api_key"][1:]
    elif api_key_env_var:
        api_key_source = api_key_env_var
    elif "/openrouter.ai/" in openai_base_url:
        # Try OPENROUTER_API_KEY if using OpenRouter
        if os.getenv("OPENROUTER_API_KEY"):
            openai_api_key = os.getenv("OPENROUTER_API_KEY")
            api_key_source = "OPENROUTER_API_KEY"
    elif not openai_api_key:
        # Fallback to environment variables
        if os.getenv("OPENAI_API_KEY"):
            openai_api_key = os.getenv("OPENAI_API_KEY")
            api_key_source = "OPENAI_API_KEY"
        elif os.getenv("OPENROUTER_API_KEY"):
            openai_api_key = os.getenv("OPENROUTER_API_KEY")
            api_key_source = "OPENROUTER_API_KEY"
    
    # Expand cache paths
    cache_repo_str = cache.get("repo", "$HOME/.cache/git-fork-recon/repos")
    cache_report_str = cache.get("report", "$HOME/.cache/git-fork-recon/reports")
    
    # Use os.path.expandvars() which handles both $HOME in paths and pure env var references
    # For pure env var references, validate they're set after expansion
    cache_repo_expanded = _expand_path(cache_repo_str)
    cache_report_expanded = _expand_path(cache_report_str)
    
    # Validate that pure env var references were resolved
    if _is_pure_env_var_reference(cache_repo_str) and cache_repo_expanded == cache_repo_str:
        env_var_name = cache_repo_str[1:]
        raise ValueError(
            f"Environment variable {env_var_name} referenced in config but not set"
        )
    if _is_pure_env_var_reference(cache_report_str) and cache_report_expanded == cache_report_str:
        env_var_name = cache_report_str[1:]
        raise ValueError(
            f"Environment variable {env_var_name} referenced in config but not set"
        )
    
    cache_repo = Path(cache_repo_expanded)
    cache_report = Path(cache_report_expanded)
    
    # Get model and context_length
    model = endpoint.get("model", "deepseek/deepseek-chat-v3-0324:free")
    context_length = endpoint.get("context_length")
    
    # Get server settings
    allowed_models_str = server.get("allowed_models")
    server_allowed_models = None
    if allowed_models_str:
        server_allowed_models = [m.strip() for m in str(allowed_models_str).split(",") if m.strip()]
    
    server_parallel_tasks = int(server.get("parallel_tasks", 2))
    server_disable_auth = server.get("disable_auth", True)
    if isinstance(server_disable_auth, str):
        server_disable_auth = server_disable_auth.lower() in ("1", "true", "yes")
    
    server_auth_bearer_token = _resolve_env_var(server.get("auth_bearer_token", "")) or None
    
    server_cache_dir_str = server.get("cache_dir")
    server_cache_dir = None
    if server_cache_dir_str:
        server_cache_dir_expanded = _expand_path(_resolve_env_var(str(server_cache_dir_str)))
        server_cache_dir = Path(server_cache_dir_expanded)
    
    server_disable_ui = server.get("disable_ui", False)
    if isinstance(server_disable_ui, str):
        server_disable_ui = server_disable_ui.lower() in ("1", "true", "yes")
    
    server_host = server.get("host", "127.0.0.1")
    server_port = int(server.get("port", 8000))
    
    # Validate required fields
    if not github_token:
        logger.error("GITHUB_TOKEN is required in config or environment")
        sys.exit(1)
    if not openai_api_key:
        logger.error("API key is required in config or environment")
        sys.exit(1)
    
    return Config.model_validate(
        {
            "github_token": github_token,
            "openai_api_key": openai_api_key,
            "api_key_source": api_key_source,
            "openai_base_url": openai_base_url,
            "cache_repo": cache_repo,
            "cache_report": cache_report,
            "model": model,
            "context_length": context_length,
            "server_allowed_models": server_allowed_models,
            "server_parallel_tasks": server_parallel_tasks,
            "server_disable_auth": server_disable_auth,
            "server_auth_bearer_token": server_auth_bearer_token,
            "server_cache_dir": server_cache_dir,
            "server_disable_ui": server_disable_ui,
            "server_host": server_host,
            "server_port": server_port,
        }
    )
