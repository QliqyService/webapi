import logging
import sys
from enum import StrEnum

from loguru import logger as LOGGER


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = LOGGER.level(record.levelname).name
        except (AttributeError, ValueError):
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        LOGGER.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class CustomLogger:
    LOGGING_LOG_LEVEL = LogLevel.DEBUG
    LOGGING_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    LOGGING_DEBUG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    @classmethod
    def make_logger(cls, debug: bool = False) -> LOGGER:
        log_format = cls.LOGGING_DEBUG_FORMAT if debug else cls.LOGGING_FORMAT
        _logger = cls.customize_logging(level=cls.LOGGING_LOG_LEVEL, logs_format=log_format)
        return _logger

    @classmethod
    def customize_logging(cls, level: str, logs_format: str) -> LOGGER:
        intercept_handler = InterceptHandler()

        LOGGER.remove()
        LOGGER.add(
            sink=sys.stdout,
            filter=lambda record: "shared/healthcheck" not in record["message"],
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=logs_format,
        )

        lognames = [
            "asyncio",
            # "aio_pika",
            "tenacity",
            "fastapi",
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "faststream",
            "faststream.rabbit",
            "faststream.broker",
            "faststream.rabbit.broker",
        ]

        for _log in lognames:
            _logger = logging.getLogger(_log)
            _logger.handlers = [intercept_handler]
            _logger.propagate = False
            _logger.setLevel(logging.DEBUG)

        return LOGGER.bind(request_id=None, method=None)
