"""
    Minimal example: run a DNP3 Master that outputs measurement data as JSON.

    This demonstrates how to swap the default SOEHandler for the JSONSOEHandler
    so that every SOE callback writes structured JSON instead of log lines.

    Usage:
        python json_master_example.py                     # JSON to stdout only
        python json_master_example.py measurements.json   # also append to file
"""

import sys

from master import MyMaster, MyLogger, AppChannelListener, MasterApplication
from json_soe_handler import JSONSOEHandler


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    soe_handler = JSONSOEHandler(output_file=output_file, stdout=True)

    print("Starting DNP3 Master with JSON SOE handler...")
    if output_file:
        print("JSON records will also be written to: {}".format(output_file))

    app = MyMaster(
        log_handler=MyLogger(),
        listener=AppChannelListener(),
        soe_handler=soe_handler,
        master_application=MasterApplication(),
    )

    print("Master is running. Press Ctrl-C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
