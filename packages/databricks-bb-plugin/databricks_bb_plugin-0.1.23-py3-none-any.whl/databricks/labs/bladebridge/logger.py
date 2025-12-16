import logging
import sys
from pathlib import Path
from typing import TextIO

import pygls.protocol.json_rpc
from databricks.labs.blueprint.logger import install_logger, NiceFormatter


def install_loggers(
    *,
    level: int | str = logging.DEBUG,
    stream: TextIO = sys.stderr,
    root: logging.Logger = logging.getLogger(),
    # TODO: This default is wrong, and is the (root?) cause for why we're logging into the source tree.
    logfile: Path = Path("lsp-server.log"),
) -> None:
    """Install loggers for the application.

    After setup, logs that reach the provided root will be written:

      - To the provided stream (default: stderr) if they are at the provided level or higher.
      - To the provided logfile (all logs, DEBUG or higher).

    Args:
      level: The minimum logging level for logs that will be written to the stream.
      stream: The stream to which logs will be written.
      root: The root logger to set up. (Default: system root logger).
      logfile: The path to which logs will also be written.
    """
    # Note: blueprint clears all handlers, making this idempotent.
    install_logger(level, stream=stream, root=root)

    file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(NiceFormatter(probe_tty=True, stream=file_handler.stream))
    root.addHandler(file_handler)
    root.setLevel(logging.DEBUG)


def adjust_pygls_logging():
    """Adjust the logging of the pygls module."""

    filter_level = logging.INFO
    filter_name = pygls.protocol.json_rpc.logger.name
    filter_functions = frozenset({"_send_data", "wrapper"})
    # Log records are associated with the name of the final .module from where they are emitted.
    filter_module_name = pygls.protocol.json_rpc.__name__.rsplit(".", maxsplit=1)[-1]

    def json_rpc_filter(record: logging.LogRecord) -> bool:
        """Adjust pygls protocol-level INFO logs to DEBUG level."""
        if (
            record.levelno == filter_level
            and record.name == filter_name
            and record.module == filter_module_name
            and record.funcName in filter_functions
        ):
            record.levelno = logging.DEBUG
            record.levelname = logging.getLevelName(record.levelno)
        return True

    pygls_logger = pygls.protocol.json_rpc.logger
    pygls_logger.addFilter(json_rpc_filter)
