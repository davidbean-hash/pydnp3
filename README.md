# pydnp3
Python bindings for the [opendnp3](https://github.com/automatak/dnp3) library, an open source
implementation of the [DNP3](http://ww.dnp.org) protocol stack written in C++14.

Note: This is a work in progress. See [Issues](https://github.com/ChargePoint/pydnp3/issues) for things we know about and feel free to add your own.

**Supported Platforms:** Linux, MacOS, Windows

> **⚠️ PyPI Package is Outdated:** The `pydnp3` package on PyPI was last updated in 2018 and only
> supports Python 2.7. It does **not** include pre-built wheels for modern Python versions or
> Windows. You **must** build from source using the instructions below to use pydnp3 with
> Python 3.x.

## Dependencies

To build the library from source, you must have:

* Python >= 3.6
* A toolchain with a C++14 compiler
* CMake >= 2.8.12 (https://cmake.org/download/)

This repository includes two repositories as submodules (under `deps/`):

* dnp3 (https://github.com/automatak/dnp3)
* pybind11 (https://github.com/Kisensum/pybind11) - This is a fork containing a minor patch
required to compile some of the pydnp3 wrapper code. It will be replaced with pybind11 proper
when the issue is resolved.

## Build & Install

At the moment, this library must be built from source:

```bash
git clone --recursive https://github.com/ChargePoint/pydnp3.git
cd pydnp3
python setup.py install
```

## Platform-Specific Installation

### Linux / Ubuntu

Install the required system packages before building:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake python3-dev git
```

Then clone and build:

```bash
git clone --recursive https://github.com/ChargePoint/pydnp3.git
cd pydnp3
git submodule init && git submodule update --recursive
python3 setup.py install
```

> **Note:** If you encounter a `LinkedList.h` compilation error (see
> [#6](https://github.com/ChargePoint/pydnp3/issues/6)), it is typically caused by the git
> submodules not being properly initialized. Make sure you either cloned with `--recursive` or
> ran `git submodule init && git submodule update --recursive` before building.

### Windows

pydnp3 can be built from source on Windows. This requires Visual Studio Build Tools with C++14
support (see [PR #13](https://github.com/ChargePoint/pydnp3/pull/13) which added Windows build
support).

**Prerequisites:**

1. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   (2017 or later) with the "Desktop development with C++" workload.
2. Install [CMake](https://cmake.org/download/) >= 3.1.0 (must be on your PATH).
3. Install Python 3.6+ (64-bit recommended).

**Build steps:**

Open a "Developer Command Prompt for Visual Studio" (or "x64 Native Tools Command Prompt") and run:

```cmd
git clone --recursive https://github.com/ChargePoint/pydnp3.git
cd pydnp3
git submodule init && git submodule update --recursive
python setup.py install
```

> **Note:** The PyPI package (`pip install pydnp3`) does **not** work on Windows
> (see [#3](https://github.com/ChargePoint/pydnp3/issues/3)). You must build from source.

### Raspberry Pi / ARM / Low-Memory Devices

On devices with limited RAM (e.g., Raspberry Pi), the C++ compilation may be killed by the
OS due to out-of-memory conditions (see [#15](https://github.com/ChargePoint/pydnp3/issues/15)).

To work around this, limit the number of parallel build jobs using the `PYDNP3_BUILD_JOBS`
environment variable:

```bash
sudo apt-get install -y build-essential cmake python3-dev git
git clone --recursive https://github.com/ChargePoint/pydnp3.git
cd pydnp3
git submodule init && git submodule update --recursive
export PYDNP3_BUILD_JOBS=1
python3 setup.py install
```

Setting `PYDNP3_BUILD_JOBS=1` forces single-threaded compilation, significantly reducing memory
usage at the cost of longer build times. You may also want to increase swap space:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### macOS

Install dependencies via Homebrew:

```bash
brew install cmake
```

Then clone and build:

```bash
git clone --recursive https://github.com/ChargePoint/pydnp3.git
cd pydnp3
git submodule init && git submodule update --recursive
python3 setup.py install
```

## Documentation

pydnp3 is a thin wrapper around most all of the opendnp3 classes. Documentation for the opendnp3
classes is available at [automatak](https://www.automatak.com/opendnp3/#documentation).

Use python's help to discover the available wrapper classes and functions. For example,

```python
>>> import pydnp3
>>> help(pydnp3.opendnp3)
Help on module pydnp3.opendnp3 in pydnp3:

NAME
    pydnp3.opendnp3 - Bindings for opendnp3 namespace

FILE
    (built-in)

CLASSES
    pybind11_builtins.pybind11_object(builtins.object)
        AnalogCommandEvent
        AnalogInfo
            AnalogSpec
...
```

