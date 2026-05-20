# pydnp3 Examples

## Overview

This directory contains example scripts demonstrating how to use the pydnp3 library:

- **master.py** - A DNP3 Master application that connects to an Outstation and performs class scans.
- **master_cmd.py** - A command-line interface for interacting with the Master.
- **outstation.py** - A DNP3 Outstation application that responds to Master requests.
- **outstation_cmd.py** - A command-line interface for interacting with the Outstation.
- **visitors.py** - Visitor pattern implementations for processing measurement data types.
- **json_visitor.py** - JSON output support for DNP3 measurement data (see below).

## JSON Output Support

The `json_visitor.py` module provides a `JSONSOEHandler` class that outputs DNP3 measurement
data as JSON from the master's class scans.

### Usage

```python
from json_visitor import JSONSOEHandler

# Output measurements as JSON to stdout
soe_handler = JSONSOEHandler()

# Output measurements as JSON to a file
soe_handler = JSONSOEHandler(output_file='measurements.json')
```

### Integration with MyMaster

Pass the `JSONSOEHandler` as the `soe_handler` parameter when creating a `MyMaster` instance:

```python
from master import MyMaster, MyLogger, AppChannelListener, MasterApplication
from json_visitor import JSONSOEHandler

app = MyMaster(
    log_handler=MyLogger(),
    listener=AppChannelListener(),
    soe_handler=JSONSOEHandler(output_file='measurements.json'),
    master_application=MasterApplication()
)
```

### Output Format

The handler produces a JSON array of measurement objects:

```json
[
  {
    "group_variation": "Group2Var1",
    "header_index": 0,
    "data_type": "ICollectionIndexedBinary",
    "index": 0,
    "value": true
  },
  {
    "group_variation": "Group30Var1",
    "header_index": 1,
    "data_type": "ICollectionIndexedAnalog",
    "index": 3,
    "value": 25.6
  }
]
```

Each measurement object contains:
- **group_variation** - The DNP3 group and variation identifier.
- **header_index** - The index of the header in the response.
- **data_type** - The collection type (e.g., `ICollectionIndexedBinary`).
- **index** - The point index within the outstation.
- **value** - The measurement value.
