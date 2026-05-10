# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-01-01

### Added
- Modern `pyproject.toml` build configuration using scikit-build-core
- GitHub Actions CI/CD pipeline for automated building and testing
- Multi-platform CI matrix (Linux, macOS) with Python 3.8-3.13 support
- Automated wheel building via cibuildwheel for PyPI releases
- Trusted Publisher PyPI publishing workflow
- Ruff linter configuration
- Quick Start section in README with usage examples
- Contributing guidelines

### Changed
- Minimum Python version raised to 3.8 (dropped Python 2.7 support)
- Updated project metadata (classifiers, URLs, maintainers)
- Modernized README with badges, improved structure, and clearer instructions
- Build system now uses scikit-build-core instead of raw setuptools + CMake

### Deprecated
- `setup.py` is retained for backward compatibility but `pyproject.toml` is the canonical build config

## [0.1.0] - 2018-06-01

### Added
- Initial release of pydnp3
- Python bindings for opendnp3 namespaces: asiodnp3, asiopal, opendnp3, openpal
- Example Master and Outstation implementations
- Integration test suite
- Support for Python 2.7, 3.5, 3.6
