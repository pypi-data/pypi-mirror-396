from logging import (
    Formatter,
    Handler,
    Logger,
    StreamHandler,
    getLogger,
)
from os import environ
from typing import Optional

__all__ = [
    "LoggerFactory",
]

ROOT_LOGGER_NAME = (
    environ.get("QENA_SHARED_LIB_LOGGING_LOGGER_NAME") or "qena_shared_lib"
)


class LoggerFactory:
    _LOGGERS: dict[str, Logger] = {}

    @classmethod
    def get_logger(cls, name: str | None = None) -> Logger:
        logger_name = ROOT_LOGGER_NAME

        if name:
            logger_name = f"{ROOT_LOGGER_NAME}.{name.strip('.')}"

        logger = getLogger(logger_name)
        handlers = [handler.__class__ for handler in logger.handlers]

        if logger.parent is not None:
            cls._check_handler(handlers=handlers, logger=logger.parent)

        if StreamHandler not in handlers:
            stream_handler = StreamHandler()

            stream_handler.setFormatter(
                Formatter(
                    "[ %(levelname)-8s] %(name)s [ %(filename)s:%(lineno)d in %(funcName)s ]  ---  %(message)s"
                )
            )
            logger.addHandler(stream_handler)

        return cls._set_and_get_logger(logger_name=logger_name, logger=logger)

    @classmethod
    def _set_and_get_logger(cls, logger_name: str, logger: Logger) -> Logger:
        if logger_name not in cls._LOGGERS:
            cls._LOGGERS[logger_name] = logger

        return cls._LOGGERS[logger_name]

    @classmethod
    def _check_handler(
        cls, handlers: list[type[Handler]], logger: Optional[Logger] = None
    ) -> None:
        if logger is None:
            return

        handlers.extend([handler.__class__ for handler in logger.handlers])
        cls._check_handler(handlers=handlers, logger=logger.parent)
