"""
    JSONSOEHandler -- an ISOEHandler that emits measurement data as JSON.

    Addresses https://github.com/ChargePoint/pydnp3/issues/23

    Usage:
        from json_soe_handler import JSONSOEHandler

        handler = JSONSOEHandler()                    # JSON to stdout
        handler = JSONSOEHandler("measurements.json") # JSON to file
        handler = JSONSOEHandler("out.json", stdout=True)  # both
"""

import json
import sys
from datetime import datetime, timezone

from pydnp3 import opendnp3
from visitors import (
    VisitorIndexedBinary,
    VisitorIndexedDoubleBitBinary,
    VisitorIndexedCounter,
    VisitorIndexedFrozenCounter,
    VisitorIndexedAnalog,
    VisitorIndexedBinaryOutputStatus,
    VisitorIndexedAnalogOutputStatus,
    VisitorIndexedTimeAndInterval,
)

VISITOR_CLASS_TYPES = {
    opendnp3.ICollectionIndexedBinary: VisitorIndexedBinary,
    opendnp3.ICollectionIndexedDoubleBitBinary: VisitorIndexedDoubleBitBinary,
    opendnp3.ICollectionIndexedCounter: VisitorIndexedCounter,
    opendnp3.ICollectionIndexedFrozenCounter: VisitorIndexedFrozenCounter,
    opendnp3.ICollectionIndexedAnalog: VisitorIndexedAnalog,
    opendnp3.ICollectionIndexedBinaryOutputStatus: VisitorIndexedBinaryOutputStatus,
    opendnp3.ICollectionIndexedAnalogOutputStatus: VisitorIndexedAnalogOutputStatus,
    opendnp3.ICollectionIndexedTimeAndInterval: VisitorIndexedTimeAndInterval,
}

DATA_TYPE_LABELS = {
    opendnp3.ICollectionIndexedBinary: "Binary",
    opendnp3.ICollectionIndexedDoubleBitBinary: "DoubleBitBinary",
    opendnp3.ICollectionIndexedCounter: "Counter",
    opendnp3.ICollectionIndexedFrozenCounter: "FrozenCounter",
    opendnp3.ICollectionIndexedAnalog: "Analog",
    opendnp3.ICollectionIndexedBinaryOutputStatus: "BinaryOutputStatus",
    opendnp3.ICollectionIndexedAnalogOutputStatus: "AnalogOutputStatus",
    opendnp3.ICollectionIndexedTimeAndInterval: "TimeAndInterval",
}


class JSONSOEHandler(opendnp3.ISOEHandler):
    """ISOEHandler that converts measurement data to JSON.

    Each Start/End cycle collects every Process() call into a single JSON
    record and writes it to stdout and/or a file.

    JSON structure per cycle::

        {
          "timestamp": "2024-01-15T12:34:56.789012+00:00",
          "headers": [
            {
              "group_variation": "Group30Var1",
              "header_index": 0,
              "data_type": "Analog",
              "measurements": [
                {"index": 0, "value": 42.0},
                {"index": 1, "value": 17.5}
              ]
            }
          ]
        }
    """

    def __init__(self, output_file=None, stdout=True):
        """
        :param output_file: Optional path to a file. Each JSON record is
                            appended as a single line (JSON Lines format).
        :param stdout:      If True (default), also print JSON to stdout.
        """
        super(JSONSOEHandler, self).__init__()
        self._output_file = output_file
        self._stdout = stdout
        self._current_headers = []

    def Start(self):
        self._current_headers = []

    def End(self):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "headers": self._current_headers,
        }
        json_str = json.dumps(record, indent=2)
        if self._stdout:
            print(json_str, file=sys.stdout)
        if self._output_file:
            with open(self._output_file, "a") as fh:
                fh.write(json.dumps(record) + "\n")
        self._current_headers = []

    def Process(self, info, values):
        """Process measurement data and collect it into the current record.

        :param info:   HeaderInfo
        :param values: A collection of indexed measurement values.
        """
        values_type = type(values)
        visitor_class = VISITOR_CLASS_TYPES.get(values_type)
        if visitor_class is None:
            return

        visitor = visitor_class()
        values.Foreach(visitor)

        data_type = DATA_TYPE_LABELS.get(values_type, values_type.__name__)
        measurements = []
        for index, value in visitor.index_and_value:
            entry = {"index": index, "value": value}
            if data_type == "TimeAndInterval":
                entry["value"] = {"dnp_time": value[0], "interval": value[1]}
            measurements.append(entry)

        self._current_headers.append({
            "group_variation": str(info.gv),
            "header_index": info.headerIndex,
            "data_type": data_type,
            "measurements": measurements,
        })
