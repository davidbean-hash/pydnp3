"""
    JSON output support for DNP3 measurement data from the master's class scans.

    This module provides a JSONSOEHandler that extends the ISOEHandler interface
    to output measurement data as JSON, either to stdout or to a file.

    Usage:
        from json_visitor import JSONSOEHandler

        # Output to stdout
        handler = JSONSOEHandler()

        # Output to a file
        handler = JSONSOEHandler(output_file='measurements.json')

    See also: GitHub issue ChargePoint/pydnp3#23
"""
import json

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


class JSONSOEHandler(opendnp3.ISOEHandler):
    """
    An ISOEHandler implementation that collects measurement data and outputs it as JSON.

    Measurements are accumulated during a Start/End cycle and then either printed
    to stdout or written to the specified output file as a JSON array.
    """

    def __init__(self, output_file=None):
        super(JSONSOEHandler, self).__init__()
        self.output_file = output_file
        self.measurements = []

    def Start(self):
        self.measurements = []

    def End(self):
        if self.output_file:
            with open(self.output_file, 'w') as f:
                json.dump(self.measurements, f, indent=2)
        else:
            print(json.dumps(self.measurements, indent=2))

    def Process(self, info, values):
        """
        Process measurement data by visiting the collection and storing results as dicts.

        :param info: HeaderInfo
        :param values: A collection of indexed measurement values.
        """
        visitor_class_types = {
            opendnp3.ICollectionIndexedBinary: VisitorIndexedBinary,
            opendnp3.ICollectionIndexedDoubleBitBinary: VisitorIndexedDoubleBitBinary,
            opendnp3.ICollectionIndexedCounter: VisitorIndexedCounter,
            opendnp3.ICollectionIndexedFrozenCounter: VisitorIndexedFrozenCounter,
            opendnp3.ICollectionIndexedAnalog: VisitorIndexedAnalog,
            opendnp3.ICollectionIndexedBinaryOutputStatus: VisitorIndexedBinaryOutputStatus,
            opendnp3.ICollectionIndexedAnalogOutputStatus: VisitorIndexedAnalogOutputStatus,
            opendnp3.ICollectionIndexedTimeAndInterval: VisitorIndexedTimeAndInterval,
        }
        visitor_class = visitor_class_types[type(values)]
        visitor = visitor_class()
        values.Foreach(visitor)
        for index, value in visitor.index_and_value:
            self.measurements.append({
                'group_variation': str(info.gv),
                'header_index': info.headerIndex,
                'data_type': type(values).__name__,
                'index': index,
                'value': value,
            })
