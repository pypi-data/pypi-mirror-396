# Development Guide

This guide is for developers who want to contribute to or modify the PyPI Package Stats package.

## Requirements

- Python 3.8+
- uv package manager (https://docs.astral.sh/uv/)

## Setup

### Clone the repository

```bash
git clone https://github.com/ysskrishna/pypi-package-stats.git
cd pypi-package-stats
```

### Install dependencies

```bash
uv sync
```

## Development Usage

### Run the tool during development

```bash
uv run pypi-package-stats package <PACKAGE_NAME>
```

Example:

```bash
uv run pypi-package-stats package requests
```

### JSON output

Get output in JSON format:

```bash
uv run pypi-package-stats package <PACKAGE_NAME> --json
```

### Cache management

#### Disable caching

```bash
uv run pypi-package-stats package <PACKAGE_NAME> --no-cache
```

#### Custom cache TTL

Set cache time-to-live in seconds (0 = disable):

```bash
uv run pypi-package-stats package <PACKAGE_NAME> --cache-ttl 7200
```

#### Clear cache

```bash
uv run pypi-package-stats cache-clear
```

#### View cache information

```bash
uv run pypi-package-stats cache-info
```

### Help

```bash
uv run pypi-package-stats --help
uv run pypi-package-stats package --help
```

