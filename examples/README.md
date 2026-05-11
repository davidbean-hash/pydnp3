# pydnp3 Examples

This directory contains example applications demonstrating how to use the pydnp3 library
to build DNP3 Master and Outstation applications.

## Table of Contents

- [File Overview](#file-overview)
- [Quick Start](#quick-start)
- [IP Configuration](#ip-configuration)
- [Polling Multiple Outstations](#polling-multiple-outstations)
- [Custom SOE Handler](#custom-soe-handler)
- [Analog Data Types Reference](#analog-data-types-reference)

---

## File Overview

| File | Description |
|------|-------------|
| `master.py` | Core master station library. Defines the `MyMaster` class, which creates a `DNP3Manager`, opens a TCP client channel, adds a master stack, and configures periodic class scans. Also provides helper classes: `MyLogger` (custom log handler), `AppChannelListener` (channel state callbacks), `SOEHandler` (processes measurement data from outstations using the Visitor pattern), and `MasterApplication` (application-layer callbacks). |
| `master_cmd.py` | Interactive command-line interface for the master. Uses Python's `cmd` module to expose commands such as `o1`/`o2`/`o3` (DirectOperate), `s1`/`s2` (SelectAndOperate), `scan_all`, `scan_range`, `scan_fast`, `scan_slow`, `write_time`, `restart`, and log-level controls. |
| `outstation.py` | Core outstation application. Defines `OutstationApplication`, which creates a `DNP3Manager`, opens a TCP server channel, adds an outstation stack, and configures the point database. Also includes `OutstationCommandHandler` (handles Select/Operate from the master), `AppChannelListener`, and `MyLogger`. |
| `outstation_cmd.py` | Interactive command-line interface for the outstation. Lets users push simulated measurements to the master: `a` (Analog), `b` (Binary), `c` (Counter), `d` (DoubleBitBinary), and shortcut commands `a2` and `b0`. |
| `visitors.py` | Visitor classes for SOE (Sequence of Events) handling. Implements `IVisitor` subclasses for every indexed data type — Binary, DoubleBitBinary, Counter, FrozenCounter, Analog, BinaryOutputStatus, AnalogOutputStatus, and TimeAndInterval. Each visitor collects `(index, value)` tuples when the master processes incoming measurements. |

---

## Quick Start

Run a master and outstation pair on the same machine using localhost.

### Prerequisites

- pydnp3 installed (`python setup.py install` from the repo root)
- Two terminal windows

### Step 1 — Start the Outstation

```bash
cd examples/
python outstation_cmd.py
```

You should see log messages ending with `Initialization complete. In command loop.` and an `outstation>` prompt.

### Step 2 — Start the Master

In a second terminal:

```bash
cd examples/
python master_cmd.py
```

You should see log messages indicating the master is connecting to `127.0.0.1:20000`, followed by a `master>` prompt. After a few seconds the channel should open and the master will begin its periodic scans.

### Step 3 — Send Data

From the **outstation** terminal, push a measurement to the master:

```
outstation> a 1 3.14
```

This sends an Analog value of `3.14` at index `1`. You should see SOE log output on the master side.

From the **master** terminal, send a command to the outstation:

```
master> o1
```

This sends a DirectOperate LATCH_ON command (BinaryOutput, group 12) at index 5.

Type `menu` in either terminal to see all available commands.

---

## IP Configuration

> Addresses issue [#27](https://github.com/ChargePoint/pydnp3/issues/27)

The master acts as a **TCP client** and connects _to_ the outstation. The outstation acts as a
**TCP server** and listens _for_ incoming connections. The key constants are:

| Constant (file) | Purpose | Default |
|---|---|---|
| `HOST` (`master.py`) | IP address the master connects **to** (the outstation's IP) | `127.0.0.1` |
| `LOCAL` (`master.py`) | Local adapter to bind the master's outgoing socket | `0.0.0.0` |
| `PORT` (`master.py`) | TCP port to connect to | `20000` |
| `LOCAL_IP` (`outstation.py`) | IP address the outstation listens on | `0.0.0.0` |
| `PORT` (`outstation.py`) | TCP port the outstation listens on | `20000` |

### Same Machine (localhost)

No changes are needed — the defaults work out of the box:

- **Outstation** listens on `0.0.0.0:20000` (all interfaces).
- **Master** connects to `127.0.0.1:20000`.

### Different Machines

Set the master's `HOST` to the **outstation machine's IP address**. The outstation's `LOCAL_IP`
should remain `0.0.0.0` so it accepts connections on all network interfaces.

**Example — two Raspberry Pis on the same network:**

| Device | Role | IP Address |
|---|---|---|
| Pi A | Outstation | `192.168.1.50` |
| Pi B | Master | `192.168.1.51` |

On **Pi A** (`outstation.py`) — no changes needed:

```python
LOCAL_IP = "0.0.0.0"   # Listen on all interfaces
PORT = 20000
```

On **Pi B** (`master.py`) — point HOST at the outstation:

```python
HOST = "192.168.1.50"  # IP address of Pi A (outstation)
LOCAL = "0.0.0.0"
PORT = 20000
```

### Firewall Note

Ensure that TCP port `20000` (or whatever port you choose) is open on the outstation machine.
On Linux you can verify with:

```bash
sudo ufw allow 20000/tcp        # if using ufw
# or
sudo iptables -A INPUT -p tcp --dport 20000 -j ACCEPT
```

---

## Polling Multiple Outstations

> Addresses issue [#21](https://github.com/ChargePoint/pydnp3/issues/21)

A single `DNP3Manager` can manage **multiple channels**, and each channel can have its own
master stack pointing at a different outstation. This avoids the overhead of creating multiple
managers.

### How It Works

1. Create **one** `DNP3Manager` (which owns the thread pool).
2. Call `manager.AddTCPClient(...)` once per outstation, providing a unique channel ID
   and the outstation's IP address.
3. On each channel, call `channel.AddMaster(...)` with the appropriate `MasterStackConfig`.
   Each outstation must have a **unique `link.RemoteAddr`** (the outstation's DNP3 link-layer
   address).

### Example Code

```python
from pydnp3 import opendnp3, openpal, asiopal, asiodnp3

# One manager for all channels — allocate enough threads for the number of channels.
manager = asiodnp3.DNP3Manager(2, asiodnp3.ConsoleLogger().Create())

retry = asiopal.ChannelRetry().Default()
listener = asiodnp3.PrintingChannelListener().Create()
soe_handler = asiodnp3.PrintingSOEHandler().Create()
master_app = asiodnp3.DefaultMasterApplication().Create()

FILTERS = opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS

# --- Outstation 1 at 192.168.1.50, DNP3 address 10 ---
channel_1 = manager.AddTCPClient("channel-1", FILTERS, retry,
                                 "192.168.1.50",   # HOST — outstation 1's IP
                                 "0.0.0.0",         # LOCAL
                                 20000,              # PORT
                                 listener)

stack_config_1 = asiodnp3.MasterStackConfig()
stack_config_1.master.responseTimeout = openpal.TimeDuration().Seconds(2)
stack_config_1.link.RemoteAddr = 10  # Outstation 1's DNP3 link-layer address

master_1 = channel_1.AddMaster("master-1", soe_handler, master_app, stack_config_1)
master_1.Enable()

# --- Outstation 2 at 192.168.1.60, DNP3 address 20 ---
channel_2 = manager.AddTCPClient("channel-2", FILTERS, retry,
                                 "192.168.1.60",   # HOST — outstation 2's IP
                                 "0.0.0.0",         # LOCAL
                                 20000,              # PORT
                                 listener)

stack_config_2 = asiodnp3.MasterStackConfig()
stack_config_2.master.responseTimeout = openpal.TimeDuration().Seconds(2)
stack_config_2.link.RemoteAddr = 20  # Outstation 2's DNP3 link-layer address

master_2 = channel_2.AddMaster("master-2", soe_handler, master_app, stack_config_2)
master_2.Enable()

# Add class scans, send commands, etc. to each master independently.
master_1.AddClassScan(opendnp3.ClassField().AllClasses(),
                      openpal.TimeDuration().Minutes(30),
                      opendnp3.TaskConfig().Default())

master_2.AddClassScan(opendnp3.ClassField().AllClasses(),
                      openpal.TimeDuration().Minutes(30),
                      opendnp3.TaskConfig().Default())
```

### Key Points

- **Thread pool size**: Pass a thread count to `DNP3Manager()` that is at least equal to
  the number of channels for optimal performance.
- **Unique channel IDs**: Each `AddTCPClient` call requires a unique string identifier
  (e.g. `"channel-1"`, `"channel-2"`).
- **Unique link addresses**: Each outstation on the network must have a distinct
  `link.RemoteAddr`. The default in the examples is `10`.
- **Independent scanning**: Each master can have its own scan schedule and command workflow.
- **SOE handlers**: You can pass a different `SOEHandler` to each master if you need
  per-outstation processing logic.

---

## Custom SOE Handler

The SOE (Sequence of Events) handler is how the master processes measurement data received
from outstations. The default `PrintingSOEHandler` just prints values to stdout. For real
applications, you will want to implement your own.

### Step 1 — Subclass `ISOEHandler`

```python
from pydnp3 import opendnp3
from visitors import *

class MySOEHandler(opendnp3.ISOEHandler):
    def __init__(self):
        super(MySOEHandler, self).__init__()

    def Process(self, info, values):
        """Called by the master when measurement data arrives."""
        # Map each collection type to its corresponding visitor
        visitor_class_types = {
            opendnp3.ICollectionIndexedBinary: VisitorIndexedBinary,
            opendnp3.ICollectionIndexedDoubleBitBinary: VisitorIndexedDoubleBitBinary,
            opendnp3.ICollectionIndexedCounter: VisitorIndexedCounter,
            opendnp3.ICollectionIndexedFrozenCounter: VisitorIndexedFrozenCounter,
            opendnp3.ICollectionIndexedAnalog: VisitorIndexedAnalog,
            opendnp3.ICollectionIndexedBinaryOutputStatus: VisitorIndexedBinaryOutputStatus,
            opendnp3.ICollectionIndexedAnalogOutputStatus: VisitorIndexedAnalogOutputStatus,
            opendnp3.ICollectionIndexedTimeAndInterval: VisitorIndexedTimeAndInterval
        }
        visitor_class = visitor_class_types[type(values)]
        visitor = visitor_class()
        values.Foreach(visitor)
        for index, value in visitor.index_and_value:
            # Replace this with your application logic — e.g. store to database,
            # publish to MQTT, trigger an alarm, etc.
            print(f"Received {type(values).__name__} index={index} value={value}")

    def Start(self):
        """Called at the start of a measurement response."""
        pass

    def End(self):
        """Called at the end of a measurement response."""
        pass
```

### Step 2 — Pass It to the Master

```python
my_soe = MySOEHandler()

master = channel.AddMaster("master",
                           my_soe,                                    # your custom handler
                           asiodnp3.DefaultMasterApplication().Create(),
                           stack_config)
```

### How the Visitor Pattern Works

When `Process()` is called, `values` is a typed collection (e.g. `ICollectionIndexedAnalog`).
You cannot iterate over it directly — instead you pass a **Visitor** object that implements
`OnValue()`. The collection calls `OnValue()` once per data point, and the visitor stores
the results.

See `visitors.py` for the full set of visitor implementations.

---

## Analog Data Types Reference

DNP3 uses Group/Variation codes to identify data types. Here are the most common analog-related
codes you will encounter in the examples:

### Static (current value) — reported on integrity polls

| Group | Variation | Type | Description |
|-------|-----------|------|-------------|
| 30 | 1 | `Group30Var1` | 32-bit Analog Input with flag |
| 30 | 2 | `Group30Var2` | 16-bit Analog Input with flag |
| 30 | 3 | `Group30Var3` | 32-bit Analog Input without flag |
| 30 | 4 | `Group30Var4` | 16-bit Analog Input without flag |
| 30 | 5 | `Group30Var5` | Single-precision float with flag |
| 30 | 6 | `Group30Var6` | Double-precision float with flag |

### Event (change) — reported on event polls

| Group | Variation | Type | Description |
|-------|-----------|------|-------------|
| 32 | 1 | `Group32Var1` | 32-bit Analog Change Event without time |
| 32 | 2 | `Group32Var2` | 16-bit Analog Change Event without time |
| 32 | 3 | `Group32Var3` | 32-bit Analog Change Event with time |
| 32 | 4 | `Group32Var4` | 16-bit Analog Change Event with time |
| 32 | 5 | `Group32Var5` | Single-precision float Change Event without time |
| 32 | 6 | `Group32Var6` | Double-precision float Change Event without time |
| 32 | 7 | `Group32Var7` | Single-precision float Change Event with time |
| 32 | 8 | `Group32Var8` | Double-precision float Change Event with time |

### Analog Output (commands from master)

| Group | Variation | Type | Description |
|-------|-----------|------|-------------|
| 41 | 1 | `AnalogOutputInt32` | 32-bit integer output |
| 41 | 2 | `AnalogOutputInt16` | 16-bit integer output |
| 41 | 3 | `AnalogOutputFloat32` | Single-precision float output |
| 41 | 4 | `AnalogOutputDouble64` | Double-precision float output |

### Binary I/O (for reference)

| Group | Variation | Type | Description |
|-------|-----------|------|-------------|
| 1 | 2 | `Group1Var2` | Binary Input with flags (static) |
| 2 | 1 | `Group2Var1` | Binary Input Change Event without time |
| 2 | 2 | `Group2Var2` | Binary Input Change Event with time |
| 12 | 1 | `CROB` | Control Relay Output Block (Binary Output command) |

### Example: Configuring Outstation Points

In `outstation.py`, the database is configured with specific Group/Variation codes:

```python
# Analog point at index 1: static = Group30Var1, event = Group32Var7
db_config.analog[1].svariation = opendnp3.StaticAnalogVariation.Group30Var1
db_config.analog[1].evariation = opendnp3.EventAnalogVariation.Group32Var7

# Binary point at index 1: static = Group1Var2, event = Group2Var2
db_config.binary[1].svariation = opendnp3.StaticBinaryVariation.Group1Var2
db_config.binary[1].evariation = opendnp3.EventBinaryVariation.Group2Var2
```
