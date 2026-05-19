import logging
import json
import time
from typing import Any


class StructuredLogger:
    """
    Structured JSON logger for observability.
    Every log entry includes: timestamp, level, service, message, context.
    """

    def __init__(self, service: str):
        self.service = service
        self._logger = logging.getLogger(service)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def _emit(self, level: str, message: str, **context):
        entry = {
            "ts": time.time(),
            "level": level,
            "service": self.service,
            "msg": message,
            **context,
        }
        getattr(self._logger, level.lower(), self._logger.info)(json.dumps(entry))

    def info(self, msg: str, **ctx): self._emit("INFO", msg, **ctx)
    def warn(self, msg: str, **ctx): self._emit("WARNING", msg, **ctx)
    def error(self, msg: str, **ctx): self._emit("ERROR", msg, **ctx)
    def debug(self, msg: str, **ctx): self._emit("DEBUG", msg, **ctx)


def get_logger(service: str) -> StructuredLogger:
    return StructuredLogger(service)
