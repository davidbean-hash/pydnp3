# pydnp3

[![CI](https://github.com/ChargePoint/pydnp3/actions/workflows/ci.yml/badge.svg)](https://github.com/ChargePoint/pydnp3/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pydnp3.svg)](https://pypi.org/project/pydnp3/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Python bindings for the [opendnp3](https://github.com/automatak/dnp3) library, an open source
implementation of the [DNP3](http://ww.dnp.org) protocol stack written in C++14.

**Supported Platforms:** Linux, macOS

## Installation

### From PyPI (recommended)

```bash
pip install pydnp3
```

### From source

**Prerequisites:**
- Python >= 3.8
- A C++14 compatible compiler (GCC >= 5, Clang >= 3.4)
- CMake >= 2.8.12

```bash
git clone --recursive https://github.com/ChargePoint/pydnp3.git
cd pydnp3
pip install .
```

> **Note:** The `--recursive` flag is required to fetch the git submodules (opendnp3 and pybind11).

For development/editable installs:

```bash
pip install -e . -v
```

## Quick Start

```python
from pydnp3 import asiodnp3, asiopal, opendnp3, openpal

# Create a DNP3 manager with 1 thread
manager = asiodnp3.DNP3Manager(1, asiodnp3.ConsoleLogger().Create())

# Connect via TCP to an outstation
channel = manager.AddTCPClient(
    "tcpclient",
    opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS,
    asiopal.ChannelRetry().Default(),
    "127.0.0.1",    # remote host
    "0.0.0.0",      # local adapter
    20000,           # port
    asiodnp3.PrintingChannelListener().Create()
)
```

See the [examples/](examples/) directory for complete Master and Outstation implementations.

## Documentation

pydnp3 is a thin wrapper around most of the opendnp3 classes. Documentation for the opendnp3
classes is available at [automatak](https://www.automatak.com/opendnp3/#documentation).

Use Python's help to discover the available wrapper classes and functions:

```python
>>> import pydnp3
>>> help(pydnp3.opendnp3)
```

## Dependencies

This repository includes two repositories as submodules (under `deps/`):

* [dnp3](https://github.com/automatak/dnp3) — The opendnp3 C++14 library
* [pybind11](https://github.com/Kisensum/pybind11) — Fork with a minor patch for pydnp3 wrapper compilation

## Development

### Running tests

```bash
pip install pytest
pytest tests/ -v
```

### Project structure

```
pydnp3/
├── src/           # C++ pybind11 binding source files
├── deps/          # Git submodules (dnp3, pybind11)
├── tests/         # Python test suite
├── examples/      # Example Master and Outstation implementations
├── CMakeLists.txt # CMake build configuration
└── pyproject.toml # Python package metadata and build config
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and add tests
4. Run the test suite: `pytest tests/ -v`
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
