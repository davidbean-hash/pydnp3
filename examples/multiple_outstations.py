"""
Example: Multiple outstations on a single DNP3Manager.

Demonstrates how to create multiple outstations, each with its own TCP channel
and channel listener. The key requirement is that all Python callback objects
(channel listeners, command handlers, outstation applications) must be stored
as instance variables to prevent garbage collection. If a Python object is GC'd
while the C++ side still holds a reference, you will see:

    "Tried to call pure virtual function IChannelListener::OnStateChange"

See: https://github.com/ChargePoint/pydnp3/issues/14
"""

import logging
import sys

from pydnp3 import opendnp3, openpal, asiopal, asiodnp3

LOG_LEVELS = opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS
LOCAL_IP = "0.0.0.0"
BASE_PORT = 20000

stdout_stream = logging.StreamHandler(sys.stdout)
stdout_stream.setFormatter(logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'))

_log = logging.getLogger(__name__)
_log.addHandler(stdout_stream)
_log.setLevel(logging.DEBUG)


class ChannelListener(asiodnp3.IChannelListener):
    """Per-outstation channel listener that logs state changes with an identifier."""

    def __init__(self, name):
        super(ChannelListener, self).__init__()
        self.name = name

    def OnStateChange(self, state):
        _log.debug('ChannelListener({}): state={}'.format(self.name, state))


class CommandHandler(opendnp3.ICommandHandler):
    """Minimal command handler for demonstration purposes."""

    def __init__(self, name):
        super(CommandHandler, self).__init__()
        self.name = name

    def Start(self):
        _log.debug('CommandHandler({}).Start'.format(self.name))

    def End(self):
        _log.debug('CommandHandler({}).End'.format(self.name))

    def Select(self, command, index):
        _log.debug('CommandHandler({}).Select: index={}'.format(self.name, index))
        return opendnp3.CommandStatus.SUCCESS

    def Operate(self, command, index, op_type):
        _log.debug('CommandHandler({}).Operate: index={}'.format(self.name, index))
        return opendnp3.CommandStatus.SUCCESS


class OutstationApp(opendnp3.IOutstationApplication):
    """Minimal outstation application for demonstration purposes."""

    def __init__(self, name):
        super(OutstationApp, self).__init__()
        self.name = name

    def ColdRestartSupport(self):
        return opendnp3.RestartMode.UNSUPPORTED

    def GetApplicationIIN(self):
        return opendnp3.ApplicationIIN()

    def SupportsAssignClass(self):
        return False

    def SupportsWriteAbsoluteTime(self):
        return False

    def SupportsWriteTimeAndInterval(self):
        return False

    def WarmRestartSupport(self):
        return opendnp3.RestartMode.UNSUPPORTED


class Outstation:
    """
    Encapsulates a single outstation with all of its associated objects.

    IMPORTANT: All callback objects (listener, command_handler, application) are stored
    as instance variables to prevent Python's garbage collector from destroying them while
    the C++ layer still holds references.
    """

    def __init__(self, manager, name, port, local_addr, remote_addr):
        self.name = name

        # Configure the outstation stack
        self.stack_config = asiodnp3.OutstationStackConfig(opendnp3.DatabaseSizes.AllTypes(10))
        self.stack_config.outstation.eventBufferConfig = opendnp3.EventBufferConfig().AllTypes(10)
        self.stack_config.outstation.params.allowUnsolicited = True
        self.stack_config.link.LocalAddr = local_addr
        self.stack_config.link.RemoteAddr = remote_addr
        self.stack_config.link.KeepAliveTimeout = openpal.TimeDuration().Max()

        # Create the channel listener -- must be stored as self.listener to avoid GC
        self.listener = ChannelListener(name)

        # Create the TCP server channel
        self.retry_parameters = asiopal.ChannelRetry().Default()
        self.channel = manager.AddTCPServer("server-{}".format(name),
                                            LOG_LEVELS,
                                            self.retry_parameters,
                                            LOCAL_IP,
                                            port,
                                            self.listener)

        # Create the command handler -- must be stored as self.command_handler to avoid GC
        self.command_handler = CommandHandler(name)

        # Create the outstation application -- must be stored as self.application to avoid GC
        self.application = OutstationApp(name)

        # Add the outstation to the channel
        self.outstation = self.channel.AddOutstation(
            "outstation-{}".format(name),
            self.command_handler,
            self.application,
            self.stack_config
        )

        # Enable the outstation to start accepting connections
        self.outstation.Enable()
        _log.debug('Outstation {} enabled on port {}, LocalAddr={}, RemoteAddr={}'.format(
            name, port, local_addr, remote_addr))


def main():
    """Create multiple outstations on a single DNP3Manager."""
    _log.debug('Creating DNP3Manager with 1 thread.')
    log_handler = asiodnp3.ConsoleLogger().Create()
    manager = asiodnp3.DNP3Manager(1, log_handler)

    # Define outstation configurations: (name, port, local_addr, remote_addr)
    outstation_configs = [
        ("outstation-1", BASE_PORT,     10, 1),
        ("outstation-2", BASE_PORT + 1, 20, 1),
        ("outstation-3", BASE_PORT + 2, 30, 1),
    ]

    # Create outstations -- store them in a list so they (and their callback objects) stay alive
    outstations = []
    for name, port, local_addr, remote_addr in outstation_configs:
        outstation = Outstation(manager, name, port, local_addr, remote_addr)
        outstations.append(outstation)

    _log.debug('All {} outstations created and enabled.'.format(len(outstations)))
    _log.debug('Press Ctrl+C to shut down.')

    try:
        # In a real application you would run your event loop here.
        # For this demo we just block until interrupted.
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        _log.debug('Shutting down...')

    manager.Shutdown()
    _log.debug('Exiting.')


if __name__ == '__main__':
    main()
