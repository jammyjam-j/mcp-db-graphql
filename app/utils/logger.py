import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional

class _JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "function": record.funcName,
            "process_id": record.process,
        }
        if record.exc_info:
            exc_type, exc_value, tb = record.exc_info
            log_record["exception"] = {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "traceback": self.formatException(record.exc_info)
            }
        return json.dumps(log_record)

def _determine_log_level() -> int:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    valid_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "WARN": logging.WARN,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET
    }
    return valid_levels.get(level_name, logging.INFO)

def _configure_root_logger() -> None:
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JSONFormatter())
        root.addHandler(handler)
        root.setLevel(_determine_log_level())

_configured = False

def get_logger(name: Optional[str] = None) -> logging.Logger:
    global _configured
    if not _configured:
        _configure_root_logger()
        _configured = True
    logger = logging.getLogger(name or __name__)
    return logger

if __name__ == "__main__":
    log = get_logger("example")
    try:
        1 / 0
    except ZeroDivisionError as e:
        log.exception("An error occurred")