import logging
from logging import LogRecord
from typing import Optional

from colorlog import ColoredFormatter

from openobd.core.session import OpenOBDSession
from openobd.core.stream_handler import StreamHandler
from openobd_protocol.Logging.Messages.LogMessage_pb2 import LogMessage, LogLevel

def initialize_logging(log_level: Optional[str]):
    if log_level is None or not isinstance(log_level, str):
        log_level = "INFO"

    handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(threadName)s: %(white)s%(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=log_level.upper())


class ScriptLogHandler(logging.Handler):
    """
    A class which sends records to an openOBD logging stream. Please note that
    formatting does not have effect on this handler. Messages are sent as-is to the engine
    and are formatted in the engine according to the rules defined server-side. This ensures a
    consistent interface for the operator.
    """
    def __init__(self, session: OpenOBDSession, level=logging.NOTSET):
        super().__init__(level)
        self.stream_handler = StreamHandler(session.open_log_stream, outgoing_stream=True)

    def close(self):
        super().close()
        self.stream_handler.stop_stream()

    def emit(self, record: LogRecord):
        self.stream_handler.send(LogMessage(
            content = record.getMessage(),
            level = self._get_grpc_level_from_name(record.levelname)
        ))

    def _get_grpc_level_from_name(self, level_name: str) -> LogLevel:
        match level_name:
            case 'CRITICAL' | 'ERROR':
                return LogLevel.LOG_LEVEL_ERROR
            case 'WARNING':
                return LogLevel.LOG_LEVEL_WARNING
            case 'DEBUG':
                return LogLevel.LOG_LEVEL_DEBUG
            case 'INFO' | 'NOTSET' | _:
                return LogLevel.LOG_LEVEL_INFO
