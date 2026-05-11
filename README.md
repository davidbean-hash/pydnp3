# pydnp3
Python bindings for the [opendnp3](https://github.com/automatak/dnp3) library,  an open source
implementation of the [DNP3](http://ww.dnp.org) protocol stack written in C++14.

Note:  This is a work in progress.  See [Issues](http://github.com/Kisensum/pydnp3/issues) for things we know about and feel free to add your own.

**Supported Platforms:** Linux, MacOS

## Getting Started

pydnp3 is a **DNP3 communication stack** for building master and outstation applications in Python. It wraps the opendnp3 C++ library via pybind11, giving you full access to the DNP3 protocol — channel configuration, data polling, control operations, and more.

> **Note:** pydnp3 is _not_ a packet parser or protocol analyzer. If you need to inspect raw DNP3 traffic from a pcap file, see the [FAQ](#faq) below.

### Quick Start

1. **Build and install** pydnp3 (see [Build & Install](#build--install) below).

2. **Start an outstation** in one terminal:

   ```bash
   cd examples
   python outstation_cmd.py
   ```

3. **Start a master** in a second terminal:

   ```bash
   cd examples
   python master_cmd.py
   ```

   The master connects to the outstation on `127.0.0.1:20000` by default. You can now send commands from the master prompt (type `menu` for options) and push simulated data from the outstation prompt.

### Examples

The [`examples/`](examples/) directory contains ready-to-run scripts:

| File | Description |
|------|-------------|
| `master.py` | Core master implementation (channel, SOE handler, callbacks) |
| `master_cmd.py` | Interactive CLI for the master — send polls, commands, and control operations |
| `outstation.py` | Core outstation implementation (database, command handler) |
| `outstation_cmd.py` | Interactive CLI for the outstation — push analog, binary, and counter values |
| `visitors.py` | Visitor pattern helpers for iterating over SOE data |

See [`examples/README.md`](examples/README.md) for detailed usage instructions, IP configuration, and multi-outstation setups.

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

## FAQ

**Q: Can I use pydnp3 to decode packets from a pcap file?**

No — pydnp3 is a DNP3 communication stack for building masters and outstations, not a packet parser. It implements the full DNP3 protocol (transport, application layer, data polling, control operations) but does not read or dissect raw packet captures.

For pcap/pcapng analysis, consider:

- [**Wireshark**](https://www.wireshark.org/) — has built-in DNP3 protocol dissection; open your capture file and filter with `dnp3`
- [**Scapy**](https://scapy.net/) — Python-based packet manipulation library with community-contributed DNP3 layers

**Q: How do I get started with DNP3 using pydnp3?**

See the [Getting Started](#getting-started) section above. In short:

1. Build and install pydnp3.
2. Run `examples/outstation_cmd.py` in one terminal (starts the outstation).
3. Run `examples/master_cmd.py` in another terminal (connects the master to the outstation).
4. See [`examples/README.md`](examples/README.md) for detailed instructions on configuration, IP setup, and advanced usage.

