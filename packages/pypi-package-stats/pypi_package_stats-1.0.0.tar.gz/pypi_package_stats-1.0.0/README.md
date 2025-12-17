# PyPI Package Stats

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
[![PyPI](https://img.shields.io/pypi/v/pypi-package-stats)](https://pypi.org/project/pypi-package-stats/)

A CLI for PyPI package stats and download analytics, built on the official pypistats API. Fetch daily, weekly, monthly, and 180-day downloads, Python version and OS breakdowns, package metadata, with flexible output (JSON or Rich console tables) and smart disk caching.

![OG Image](https://raw.githubusercontent.com/ysskrishna/pypi-package-stats/main/media/og.png)

## Features

- **Package Metadata**: Name, version, description, author, license, home page, and PyPI URL
- **Download Statistics**: Last day, week, month, and 180-day download counts
- **Python Version Breakdown**: Top 5 Python versions with download percentages (last 30 days)
- **Operating System Distribution**: Top 4 operating systems with download percentages (last 30 days)
- **JSON Output**: Optional JSON format for programmatic use
- **Intelligent Caching**: Persistent disk cache with configurable TTL (default: 1 hour)
- **Cache Management**: Clear cache and view cache information
- **Rich Terminal Output**: Beautiful formatted tables using Rich library

## Requirements

- Python 3.8+

## Installation

Install directly from PyPI:

```bash
pip install pypi-package-stats
```

## Usage

### Get package statistics

```bash
pypi-package-stats package <PACKAGE_NAME>
```

Example:

```bash
pypi-package-stats package requests
```

### JSON output

Get output in JSON format:

```bash
pypi-package-stats package <PACKAGE_NAME> --json
# or
pypi-package-stats package <PACKAGE_NAME> -j
```

### Cache management

#### Disable caching

```bash
pypi-package-stats package <PACKAGE_NAME> --no-cache
```

#### Custom cache TTL

Set cache time-to-live in seconds (0 = disable):

```bash
pypi-package-stats package <PACKAGE_NAME> --cache-ttl 7200
```

#### Clear cache

```bash
pypi-package-stats cache-clear
```

#### View cache information

```bash
pypi-package-stats cache-info
```

### Help

```bash
pypi-package-stats --help
```

## Output

The tool displays:

1. **Package Information**
   - Name and version
   - Upload time
   - Description
   - Author
   - License
   - Home page
   - PyPI URL

2. **Download Statistics** (excluding mirrors)
   - Last day
   - Last week
   - Last month
   - Last 180 days

3. **Top 5 Python Versions** (last 30 days)
   - Version number
   - Percentage of downloads
   - Total downloads

4. **Top Operating Systems** (last 30 days)
   - OS name
   - Percentage of downloads
   - Total downloads

## Caching

The tool uses persistent disk caching to reduce API calls and improve performance. Cache is stored in a platform-specific directory managed by the `platformdirs` library:

- **macOS**: `~/Library/Caches/pypipackagestats/pypipackagestats/api_cache`
- **Linux**: `~/.cache/pypipackagestats/pypipackagestats/api_cache`
- **Windows**: `%LOCALAPPDATA%\pypipackagestats\pypipackagestats\api_cache`

Default cache TTL is 3600 seconds (1 hour). You can customize this or disable caching entirely.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any issues or have feature requests, please open an issue on [GitHub](https://github.com/ysskrishna/pypi-package-stats/issues).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes and version history.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Y. Siva Sai Krishna**

- GitHub: [@ysskrishna](https://github.com/ysskrishna)
- LinkedIn: [ysskrishna](https://linkedin.com/in/ysskrishna)


