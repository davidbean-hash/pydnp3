# pydnp3 Examples

Comprehensive documentation for the pydnp3 example scripts, addressing common questions about usage, IP configuration, and polling multiple outstations.

> **Related issues:** [#25](https://github.com/ChargePoint/pydnp3/issues/25), [#27](https://github.com/ChargePoint/pydnp3/issues/27), [#21](https://github.com/ChargePoint/pydnp3/issues/21)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [IP Configuration](#ip-configuration)
5. [Polling Multiple Outstations](#polling-multiple-outstations)
6. [Available Examples](#available-examples)
7. [Command Reference](#command-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview

[DNP3](http://www.dnp.org) (Distributed Network Protocol 3) is a set of communication protocols used between components in process automation systems, most commonly in utilities such as electric and water companies. It was developed for communication between substations and control centers in SCADA (Supervisory Control and Data Acquisition) systems.

The pydnp3 library provides Python bindings for the [opendnp3](https://github.com/automatak/dnp3) C++14 library. These examples demonstrate how to:

- **Master station**: Connect to one or more outstations, poll for data, and issue control commands (Direct Operate, Select-and-Operate).
- **Outstation**: Listen for incoming master connections, respond to data requests, and accept control commands.
- **Visitor pattern**: Process heterogeneous measurement data (Binary, Analog, Counter, etc.) received from outstations.

The examples implement the DNP3 Application Layer as described in the DNP3 specification (sections 5.1.6.1–5.1.6.3), providing callback-driven interfaces for both master and outstation roles.

---

## Prerequisites

- **Python 2.7 or 3.x** (Python 3 recommended)
- **pydnp3** installed — build from source:
  ```bash
  git clone --recursive https://github.com/Kisensum/pydnp3
  cd pydnp3
  python setup.py install
  ```
- **C++14 compiler** and **CMake >= 2.8.12** (required to build from source)
- **Supported platforms:** Linux, macOS

---

## Quick Start

The simplest way to get started is to run a master and outstation pair on the same machine.

### Step 1: Start the Outstation

Open a terminal and run:

```bash
cd examples/
python outstation_cmd.py
```

You should see log output indicating the outstation has started and is listening for connections:

```
Welcome to the outstation request command line. Supported commands include:
    a       Analog measurement. Enter index and value as arguments.
    ...
outstation>
```

### Step 2: Start the Master

Open a **second terminal** and run:

```bash
cd examples/
python master_cmd.py
```

The master will connect to the outstation. You should see channel state changes and integrity poll results in both terminals:

```
Welcome to the DNP3 master request command line. Supported commands include:
    ...
master>
```

### Step 3: Send Data

In the **outstation** terminal, send an analog value:

```
outstation> a 1 42.5
```

The master will log the received measurement through the SOE (Sequence of Events) handler.

In the **master** terminal, send a control command:

```
master> o1
```

This sends a DirectOperate LATCH_ON command to the outstation.

---

## IP Configuration

The examples use three network variables to configure connections. Understanding these is essential for both local testing and remote deployments.

### Variables

| Variable | File | Default | Description |
|----------|------|---------|-------------|
| `HOST` | `master.py` | `127.0.0.1` | Remote IP address the master connects **to** (i.e., the outstation's address) |
| `LOCAL` | `master.py` | `0.0.0.0` | Local adapter address the master binds to for outgoing connections |
| `LOCAL_IP` | `outstation.py` | `0.0.0.0` | Local adapter address the outstation listens on |
| `PORT` | both | `20000` | TCP port used for the DNP3 connection |

### Local Testing (Same Machine)

No changes are needed. The defaults work out of the box:

```python
# master.py
HOST = "127.0.0.1"    # Connect to localhost (where the outstation is)
LOCAL = "0.0.0.0"      # Bind to all local interfaces
PORT = 20000

# outstation.py
LOCAL_IP = "0.0.0.0"   # Listen on all interfaces
PORT = 20000
```

### Remote Connection (Separate Machines)

When the master and outstation are on different machines:

**On the Outstation machine** (e.g., IP `192.168.1.100`):

```python
# outstation.py — no changes needed
LOCAL_IP = "0.0.0.0"   # Listen on all interfaces (recommended)
PORT = 20000
```

Setting `LOCAL_IP` to `0.0.0.0` means the outstation accepts connections on any network interface. Alternatively, you can bind to a specific interface:

```python
LOCAL_IP = "192.168.1.100"  # Only listen on this specific interface
```

**On the Master machine:**

```python
# master.py — update HOST to point to the outstation
HOST = "192.168.1.100"  # IP address of the outstation machine
LOCAL = "0.0.0.0"       # Bind to all local interfaces
PORT = 20000
```

### Common Network Setups

#### Two machines on the same LAN

```
Master (192.168.1.50)  ──TCP:20000──▶  Outstation (192.168.1.100)

master.py:   HOST = "192.168.1.100", LOCAL = "0.0.0.0", PORT = 20000
outstation.py: LOCAL_IP = "0.0.0.0", PORT = 20000
```

#### Master connecting over a VPN or WAN

```
Master (10.0.0.5)  ──VPN/WAN──▶  Outstation (10.0.1.20)

master.py:   HOST = "10.0.1.20", LOCAL = "0.0.0.0", PORT = 20000
outstation.py: LOCAL_IP = "0.0.0.0", PORT = 20000
```

Ensure that port `20000` (or whichever port you use) is open on any firewalls between the two machines.

#### Multiple outstations on the same machine (different ports)

```python
# outstation_1.py
LOCAL_IP = "0.0.0.0"
PORT = 20000

# outstation_2.py
LOCAL_IP = "0.0.0.0"
PORT = 20001
```

---

## Polling Multiple Outstations

A single master can poll multiple outstations. Each outstation requires its own **channel** (TCP connection) with a unique HOST:PORT combination.

### Approach: One Channel per Outstation

Each outstation gets its own TCP channel on the master. Create multiple channels via the `DNP3Manager`, each pointing to a different outstation:

```python
from pydnp3 import opendnp3, openpal, asiopal, asiodnp3

# Create a single DNP3Manager (shared across all channels)
manager = asiodnp3.DNP3Manager(1, asiodnp3.ConsoleLogger().Create())

retry = asiopal.ChannelRetry().Default()
listener = asiodnp3.PrintingChannelListener().Create()
filters = opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS

# Channel to Outstation 1 at 192.168.1.100:20000
channel_1 = manager.AddTCPClient("tcpclient-outstation1",
                                  filters,
                                  retry,
                                  "192.168.1.100",   # HOST for outstation 1
                                  "0.0.0.0",          # LOCAL
                                  20000,               # PORT
                                  listener)

# Channel to Outstation 2 at 192.168.1.101:20000
channel_2 = manager.AddTCPClient("tcpclient-outstation2",
                                  filters,
                                  retry,
                                  "192.168.1.101",   # HOST for outstation 2
                                  "0.0.0.0",          # LOCAL
                                  20000,               # PORT
                                  listener)

# Configure and add a master to each channel
stack_config = asiodnp3.MasterStackConfig()
stack_config.master.responseTimeout = openpal.TimeDuration().Seconds(2)
stack_config.link.RemoteAddr = 10

soe_handler = asiodnp3.PrintingSOEHandler().Create()
master_app = asiodnp3.DefaultMasterApplication().Create()

master_1 = channel_1.AddMaster("master-1", soe_handler, master_app, stack_config)
master_2 = channel_2.AddMaster("master-2", soe_handler, master_app, stack_config)

# Add scans to each master independently
scan_1 = master_1.AddClassScan(opendnp3.ClassField().AllClasses(),
                                openpal.TimeDuration().Minutes(30),
                                opendnp3.TaskConfig().Default())

scan_2 = master_2.AddClassScan(opendnp3.ClassField().AllClasses(),
                                openpal.TimeDuration().Minutes(30),
                                opendnp3.TaskConfig().Default())

# Enable both masters
master_1.Enable()
master_2.Enable()
```

### Key Points

- **One `DNP3Manager`** is sufficient for all channels. The thread pool it manages handles I/O for all channels.
- **Each outstation needs its own channel** — you cannot add two outstations to the same channel if they are on different hosts.
- **Channel names must be unique** (e.g., `"tcpclient-outstation1"`, `"tcpclient-outstation2"`).
- **Master names must be unique** within each channel.
- **Link-layer addresses** (`stack_config.link.RemoteAddr` and `LocalAddr`) must match between master and outstation pairs. The default example uses `RemoteAddr = 10` on the master and `LocalAddr = 10` on the outstation.
- For **custom SOE handling** per outstation, pass a different `SOEHandler` instance to each `AddMaster` call.

### Scaling Considerations

- Increase the thread count in `DNP3Manager(N, ...)` if you are polling many outstations (e.g., `N = 4` for dozens of outstations).
- Each channel maintains its own TCP connection and retry logic independently.

---

## Available Examples

### `master.py`

The core master implementation. Defines the following classes:

| Class | Description |
|-------|-------------|
| `MyMaster` | Main master class. Creates a `DNP3Manager`, opens a TCP client channel, adds a master to the channel, and configures periodic class scans (slow: every 30 min, fast: every 1 min). Provides methods for Direct Operate and Select-and-Operate commands. |
| `MyLogger` | Custom `ILogHandler` implementation for application-specific logging. |
| `AppChannelListener` | Custom `IChannelListener` that logs channel state changes (e.g., OPENING, OPEN, CLOSED). |
| `SOEHandler` | Custom `ISOEHandler` that processes incoming measurement data using the Visitor pattern. Handles Binary, Analog, Counter, DoubleBitBinary, FrozenCounter, BinaryOutputStatus, AnalogOutputStatus, and TimeAndInterval values. |
| `MasterApplication` | Custom `IMasterApplication` with callbacks for connection lifecycle events (OnOpen, OnClose), IIN receipt, and task lifecycle (OnTaskStart, OnTaskComplete). |

Standalone functions:

| Function | Description |
|----------|-------------|
| `command_callback` | Callback invoked when a command operation (Direct Operate or Select-and-Operate) completes. Prints the task result summary. |
| `restart_callback` | Callback invoked when a cold restart request completes. |
| `collection_callback` | Callback for individual command point results within a command task. |

### `master_cmd.py`

Interactive command-line interface for the master. Wraps `MyMaster` with a `cmd.Cmd`-based shell. See [Command Reference — Master Commands](#master-commands) for all available commands.

Run with:

```bash
python master_cmd.py
```

### `outstation.py`

The core outstation implementation. Defines the following classes:

| Class | Description |
|-------|-------------|
| `OutstationApplication` | Main outstation class. Extends `IOutstationApplication`. Creates a `DNP3Manager`, opens a TCP server channel, adds an outstation, and configures a database with 10 points each of Analog, Binary, Counter, etc. Specifically configures Analog indexes 1–2 and Binary indexes 1–2 as Class 2 data. Provides `apply_update()` to push new values to the master. |
| `OutstationCommandHandler` | Custom `ICommandHandler` that processes Select and Operate requests from the master. Returns `SUCCESS` for all commands. |
| `AppChannelListener` | Custom `IChannelListener` for outstation-side channel state change logging. |
| `MyLogger` | Custom `ILogHandler` for outstation-side logging. |

Key configuration (in `configure_stack()`):

- **Database size:** 10 points of each type (Analog, Binary, Counter, etc.)
- **Event buffer:** 10 events per type
- **Unsolicited responses:** Enabled (`allowUnsolicited = True`)
- **Link-layer addresses:** `LocalAddr = 10`, `RemoteAddr = 1`
- **Keep-alive timeout:** Maximum (no timeout)

### `outstation_cmd.py`

Interactive command-line interface for the outstation. Wraps `OutstationApplication` with a `cmd.Cmd`-based shell. See [Command Reference — Outstation Commands](#outstation-commands) for all available commands.

Run with:

```bash
python outstation_cmd.py
```

### `visitors.py`

Implements the **Visitor pattern** for processing heterogeneous measurement data received from outstations. The master's `SOEHandler.Process()` method uses these visitors to iterate over collections of indexed data values.

Each visitor class extends the corresponding `IVisitorIndexed*` interface and accumulates `(index, value)` tuples in an `index_and_value` list:

| Visitor Class | Data Type | DNP3 Group |
|---------------|-----------|------------|
| `VisitorIndexedBinary` | Binary Input | Group 1/2 |
| `VisitorIndexedDoubleBitBinary` | Double-Bit Binary Input | Group 3/4 |
| `VisitorIndexedCounter` | Counter | Group 20/22 |
| `VisitorIndexedFrozenCounter` | Frozen Counter | Group 21/23 |
| `VisitorIndexedAnalog` | Analog Input | Group 30/32 |
| `VisitorIndexedBinaryOutputStatus` | Binary Output Status | Group 10/11 |
| `VisitorIndexedAnalogOutputStatus` | Analog Output Status | Group 40/42 |
| `VisitorIndexedTimeAndInterval` | Time and Interval | Group 50 |

---

## Command Reference

### Master Commands

These commands are available at the `master>` prompt when running `master_cmd.py`:

| Command | Description |
|---------|-------------|
| `chan_log_all` | Set the channel log level to `ALL_COMMS` (verbose logging). |
| `chan_log_normal` | Set the channel log level to `NORMAL`. |
| `disable_unsol` | Send a DISABLE_UNSOLICITED function to the outstation (disables unsolicited responses for Class 2, 3, and 4 events). |
| `help` | Display Python `cmd` module help for all commands. |
| `mast_log_all` | Set the master log level to `ALL_COMMS` (verbose logging). |
| `mast_log_normal` | Set the master log level to `NORMAL`. |
| `menu` | Display the command menu. |
| `o1` | **Direct Operate** — Send a `LATCH_ON` BinaryOutput (Group 12) command to index 5. |
| `o2` | **Direct Operate** — Send an AnalogOutput (Group 41) value of `7` to index 10. |
| `o3` | **Direct Operate** — Send a CommandSet with `LATCH_ON` at index 0 and `LATCH_OFF` at index 1. |
| `restart` | Request the outstation to perform a **cold restart**. |
| `s1` | **Select-and-Operate** — Send a `LATCH_ON` BinaryOutput (Group 12) command to index 8. |
| `s2` | **Select-and-Operate** — Send a CommandSet with `LATCH_ON` at index 0. |
| `scan_all` | Read all objects of Group 2 Variation 1 (Binary Input events) via `ScanAllObjects`. |
| `scan_fast` | Demand immediate execution of the fast scan (Class 1 events, normally every 1 minute). |
| `scan_range` | Perform an ad-hoc `ScanRange` of Group 1 Variation 2 (Binary Input), indexes 0–3. |
| `scan_slow` | Demand immediate execution of the slow scan (all classes, normally every 30 minutes). |
| `write_time` | Write a `TimeAndInterval` value (current time, 100-second interval) to index 0. |
| `quit` | Shut down the master and exit. |

### Outstation Commands

These commands are available at the `outstation>` prompt when running `outstation_cmd.py`:

| Command | Syntax | Description |
|---------|--------|-------------|
| `a` | `a <index> <value>` | Send an AnalogInput (Group 32) measurement. `<value>` is a float. |
| `a2` | `a2` | Send a preset AnalogInput value of `2` at index `4`. |
| `b` | `b <index> <true\|false>` | Send a BinaryInput (Group 2) measurement. |
| `b0` | `b0` | Send a preset BinaryInput value of `False` at index `6`. |
| `c` | `c <index> <value>` | Send a Counter (Group 22) measurement. `<value>` is an integer. |
| `d` | `d <index>` | Send a DoubleBitBinaryInput (Group 4) value of `DETERMINED_ON`. |
| `menu` | `menu` | Display the command menu. |
| `quit` | `quit` | Shut down the outstation and exit. |

---

## Troubleshooting

### Connection Refused / Timeout

**Symptom:** The master cannot connect to the outstation.

**Solutions:**
- Ensure the outstation is running **before** starting the master.
- Verify that `HOST` in `master.py` matches the IP address of the machine running the outstation.
- Verify that `PORT` is the same in both `master.py` and `outstation.py`.
- Check firewall rules: `sudo ufw allow 20000/tcp` (Linux) or equivalent.
- If connecting remotely, ensure the outstation's `LOCAL_IP` is `0.0.0.0` (listen on all interfaces) or the correct interface address.

### Channel State Cycling (OPENING → CLOSED → OPENING)

**Symptom:** The master log repeatedly shows the channel cycling between OPENING and CLOSED.

**Solutions:**
- The outstation is not running or is unreachable. Start the outstation first.
- There is a link-layer address mismatch. Ensure `master.py`'s `stack_config.link.RemoteAddr` matches `outstation.py`'s `stack_config.link.LocalAddr` (default is `10`).
- The master's `stack_config.link.LocalAddr` (default `1`) must match the outstation's `stack_config.link.RemoteAddr` (default `1`).

### No Data Received by Master

**Symptom:** The master connects but never receives measurement data.

**Solutions:**
- Send data from the outstation using the `outstation_cmd.py` commands (e.g., `a 1 42.5`).
- Check that you are using a custom `SOEHandler` (not the default `PrintingSOEHandler`) if you need to process data programmatically. The `PrintingSOEHandler` only prints to stdout.
- Ensure the data index you are sending matches a configured database point. The default outstation database configures 10 points of each type (indexes 0–9).
- Trigger a scan from the master: use `scan_slow` or `scan_fast` at the `master>` prompt to poll immediately.

### ImportError: No module named 'pydnp3'

**Symptom:** Running any example fails with an import error.

**Solutions:**
- Ensure pydnp3 is installed: `python setup.py install` from the repository root.
- If using a virtual environment, ensure it is activated.
- Verify the build succeeded — a C++14 compiler and CMake are required.

### ImportError: cannot import name from 'master' / 'outstation'

**Symptom:** Running `master_cmd.py` or `outstation_cmd.py` fails because it cannot import from `master` or `outstation`.

**Solutions:**
- Run the scripts from the `examples/` directory so Python can find the sibling modules:
  ```bash
  cd examples/
  python master_cmd.py
  ```
- Alternatively, add the `examples/` directory to your `PYTHONPATH`:
  ```bash
  export PYTHONPATH=/path/to/pydnp3/examples:$PYTHONPATH
  python master_cmd.py
  ```

### Response Timeout

**Symptom:** The master logs `RESPONSE_TIMEOUT` for task completions.

**Solutions:**
- The default response timeout is 2 seconds (`stack_config.master.responseTimeout`). For high-latency connections, increase it:
  ```python
  stack_config.master.responseTimeout = openpal.TimeDuration().Seconds(10)
  ```
- Ensure the outstation is running and the connection is established (check for `OPEN` channel state).

### Address Mismatch Errors

**Symptom:** The connection appears established but requests get no response.

**Solutions:**
- DNP3 uses link-layer addressing. The addresses must match:
  - Master's `RemoteAddr` (default `10`) must equal Outstation's `LocalAddr` (default `10`)
  - Master's `LocalAddr` (default `1`) must equal Outstation's `RemoteAddr` (default `1`)
- You can verify/change these in the `stack_config.link` object:
  ```python
  # master.py
  stack_config.link.RemoteAddr = 10  # Must match outstation's LocalAddr
  stack_config.link.LocalAddr = 1    # Must match outstation's RemoteAddr

  # outstation.py
  stack_config.link.LocalAddr = 10   # Must match master's RemoteAddr
  stack_config.link.RemoteAddr = 1   # Must match master's LocalAddr
  ```
