# pydnp3
Python bindings for the [opendnp3](https://github.com/automatak/dnp3) library,  an open source
implementation of the [DNP3](http://ww.dnp.org) protocol stack written in C++14.

Note:  This is a work in progress.  See [Issues](http://github.com/Kisensum/pydnp3/issues) for things we know about and feel free to add your own.

**Supported Platforms:** Linux, MacOS

## Dependencies
To build the library from source, you must have:

* A toolchain with a C++14 compiler
* CMake >= 2.8.12 (https://cmake.org/download/)

This repository includes two repositories as submodules (under `deps/`):

* dnp3 (https://github.com/automatak/dnp3)
* pybind11 (https://github.com/Kisensum/pybind11) - This is a fork containing a minor patch
required to compile some of the pydnp3 wrapper code. It will be replaced with pybind11 proper
when the issue is resolved.

## Build & Install
At the moment, this library must be built from source:
```
    $ clone --recursive http://github.com/Kisensum/pydnp3
    $ cd pydnp3
    $ python setup.py install
```


## Troubleshooting

### Build fails on Python >= 3.10

Older versions of `setup.py` used `distutils.version.LooseVersion`, which was deprecated in
Python 3.10 and removed in Python 3.12. This has been fixed by replacing it with a simple
tuple-based version comparison that works on all Python versions.

### Build fails on Raspberry Pi (out of memory)

The default parallel compilation (`-j2`) can exhaust memory on devices with limited RAM such as
the Raspberry Pi. You can control the number of parallel build jobs with the `PYDNP3_BUILD_JOBS`
environment variable:

```
PYDNP3_BUILD_JOBS=1 python setup.py install
```

On ARM platforms (`armv*` / `aarch64`), the build defaults to `-j1` automatically.

Additional tips for memory-constrained devices:

* **Increase swap space** to give the compiler more virtual memory:
  ```
  sudo fallocate -l 1G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

* **Use `MinSizeRel` build type** to reduce compiler memory usage:
  ```
  CMAKE_BUILD_TYPE=MinSizeRel PYDNP3_BUILD_JOBS=1 python setup.py install
  ```

## Documentation

pydnp3 is a thin wrapper around most all of the opendnp3 classes.  Documentation for the opendnp3
classes is available at [automatak](https://www.automatak.com/opendnp3/#documentation).

Use python's help to discover the available wrapper classes and functions.  For example,

```
> import pydnp3
> help (pydnp3.opendnp3)
Help on module pydnp3.opendnp3 in pydnp3:

NAME
    pydnp3.opendnp3 - Bindings for opendnp3 namespace

FILE
    (built-in)

CLASSES
    pybind11_builtins.pybind11_object(__builtin__.object)
        AnalogCommandEvent
        AnalogInfo
            AnalogSpec
...
```

