# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Added
- Initial release of PyPI Package Stats
- CLI tool to fetch comprehensive PyPI package information
- Package metadata display:
  - Name, version, upload time
  - Description, author, license
  - Home page and PyPI URL
- Download statistics:
  - Last day, week, month, and 180-day download counts
  - Excludes mirror downloads
- Python version breakdown:
  - Top 5 Python versions (last 30 days)
  - Download percentages and counts
- Operating system distribution:
  - Top 4 operating systems (last 30 days)
  - Download percentages and counts
- JSON output format option
- Persistent disk caching with configurable TTL (default: 3600 seconds)
- Cache management commands:
  - Clear cache
  - View cache information
- Rich terminal output with formatted tables
- Support for Python 3.8+

[1.0.0]: https://github.com/ysskrishna/pypi-package-stats/releases/tag/v1.0.0

