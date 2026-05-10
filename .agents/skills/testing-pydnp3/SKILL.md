---
name: testing-pydnp3
description: Test the pydnp3 C++/Python DNP3 bindings library end-to-end. Use when verifying build system, imports, or test suite changes.
---

# Testing pydnp3

## Prerequisites

- System packages: `cmake`, `g++`, `ninja-build`
- Python packages: `scikit-build-core`, `pybind11>=2.11,<3`, `pytest`, `ruff`, `build`
- Git submodules must be initialized: `git submodule update --init --recursive`

## Build

```bash
pip install .
# Or for wheel building:
python -m build --wheel
```

The build uses scikit-build-core as the backend, which invokes CMake to compile the C++ opendnp3 library and pybind11 bindings.

## pybind11 Version Constraint

pybind11 must be pinned to `>=2.11,<3`. Version 3.x has stricter aggregate initialization requirements that are incompatible with some opendnp3 C++ structs (e.g., `LinkStatistics::Parser`, `IndexConfig`, `OutstationParams`). This may change if the upstream C++ code is updated.

## Running Tests

```bash
pytest tests/ -v --tb=short
```

- **Expected**: 33 passed, 4 deselected
- The 4 deselected tests are marked `@pytest.mark.known_crash` (issue #34: pybind11::cast_error on SelectAndOperate/DirectOperate commands)
- **Bus error (exit 135) or Segfault (exit 139) on process exit** is a pre-existing opendnp3 C++ memory cleanup issue — all tests pass before this occurs. This is NOT a test failure.

## Import Verification

The library exposes 4 namespace modules:

```python
from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
```

All 4 should import without error. Core objects to smoke-test:

```python
manager = asiodnp3.DNP3Manager(1)
retry = asiopal.ChannelRetry.Default()
master_config = asiodnp3.MasterStackConfig()
outstation_config = asiodnp3.OutstationStackConfig(opendnp3.DatabaseSizes.AllTypes(10))
manager.Shutdown()
```

Note: `manager.Shutdown()` or process exit may trigger a "double free" / Bus error — this is the same pre-existing C++ cleanup issue.

## Linting

```bash
ruff check tests/ examples/
ruff format --check tests/ examples/
```

## CI

GitHub Actions CI runs on Ubuntu 22.04/24.04 × Python 3.9-3.13. macOS is not currently supported due to Apple Clang's strict aggregate initialization rules being incompatible with opendnp3 C++ structs.

## Wheel Metadata

After installing, verify with `pip show pydnp3`:
- Name: pydnp3
- Version: 0.2.0
- License: Apache-2.0

## Testing Approach

This is a C++ library with no GUI — all testing is shell-based. No screen recording needed. Key test flow:

1. Uninstall existing package
2. Rebuild from source (`pip install .`)
3. Verify all 4 namespace imports
4. Instantiate core DNP3 objects
5. Run full test suite
6. Verify wheel metadata
7. Optionally build wheel via `python -m build --wheel`

## Devin Secrets Needed

No secrets required for building or testing locally. PyPI publishing requires a PyPI API token (configured as a GitHub Actions secret or trusted publisher).