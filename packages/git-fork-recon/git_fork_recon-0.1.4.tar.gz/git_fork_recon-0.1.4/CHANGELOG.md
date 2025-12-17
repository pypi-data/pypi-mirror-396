# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4]

### Added
- `git-fork-recon-server` - local web frontend with REST API
  - Authentication middleware with Bearer token support
  - Versioned report caching and metadata tracking
  - Asynchronous background task management and concurrency limiting via PARALLEL_TASKS environment variable
  - Health check endpoints (/health and /health/ready)
- Support for multiple output formats (markdown, json, html, pdf)
- Include generated date variable in report templates
- Model validation against ALLOWED_MODELS environment variable
- Cross-platform cache directories using platformdirs
- uv sync instructions for modern dependency management
- Interactive configuration setup wizard using rich for first-time configuration
- TOML-based configuration file stored in platformdirs (replaces .env files)
- Environment variable references in config file (e.g., `$OPENAI_BASE_URL`)
- `--config` CLI option to specify custom config file location

### Changed
- Refactored main.py to separate analysis logic from output generation
- Enhanced error handling and status tracking
- Updated PyGithub to v2.8.1+ for rate limit API compatibility
- Migrated from single CACHE_DIR to separate REPO_CACHE_DIR and REPORT_CACHE_DIR
- Updated repository cache structure from dashes to {owner}/{repo} format
- **BREAKING**: Migrated from `.env` file to TOML config file (`config.toml` in platformdirs)
- **BREAKING**: Renamed `OPENAI_API_BASE_URL` to `OPENAI_BASE_URL` in config
- **BREAKING**: Replaced `--env-file` CLI option with `--config` option
- Renamed `cache_dir` to `cache_repo` and added `cache_report` in config structure

### Fixed
- Fixed openrouter dependency version (was pinned to non-existant version).

## [0.1.3]

### Fixed
- Don't attempt to summarize an empty list of forks to prevent hallucinations

## [0.1.2]

### Fixed
- Further fixes to .env file loading

## [0.1.1]

### Added
- Initial release with core functionality
- GitHub repository fork analysis
- LLM-powered summaries
- Caching system
- CLI interface
- Docker support