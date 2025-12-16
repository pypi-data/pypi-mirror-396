from asyncio import (
    Future,
    Queue,
    QueueFull,
    Task,
    gather,
)
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from sys import exc_info
from traceback import format_exception

from prometheus_client import Counter
from prometheus_client import Enum as PrometheusEnum

from ..logging import LoggerFactory
from ..utils import AsyncEventLoopMixin

__all__ = [
    "BaseRemoteLogSender",
    "LogLevel",
    "RemoteLogRecord",
]


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class RemoteLogRecord:
    def __init__(
        self,
        message: str,
        service_name: str,
        log_level: LogLevel,
        log_logger: str,
    ):
        self._message = message
        self._service_name = service_name
        self._log_level = log_level
        self._log_logger = log_logger
        self._tags: list[str] | None = None
        self._extra: dict[str, str] | None = None
        self._error_type: str | None = None
        self._error_message: str | None = None
        self._error_stack_trace: str | None = None
        self._created_time = datetime.now()
        self._log_retries = 0

    @property
    def message(self) -> str:
        return self._message

    @property
    def service_name(self) -> str:
        return self._service_name

    @property
    def log_level(self) -> LogLevel:
        return self._log_level

    @property
    def log_logger(self) -> str:
        return self._log_logger

    @property
    def tags(self) -> list[str] | None:
        return self._tags

    @tags.setter
    def tags(self, tags: list[str]) -> None:
        self._tags = tags

    @property
    def extra(self) -> dict[str, str] | None:
        return self._extra

    @extra.setter
    def extra(self, extra: dict[str, str]) -> None:
        self._extra = extra

    @property
    def error(self) -> tuple[str | None, str | None, str | None]:
        return self._error_type, self._error_message, self._error_stack_trace

    @property
    def log_retries(self) -> int:
        return self._log_retries

    @log_retries.setter
    def log_retries(self, log_retries: int) -> None:
        self._log_retries = log_retries

    @property
    def created_time(self) -> datetime:
        return self._created_time

    def error_from_exception(self, exception: BaseException) -> None:
        self._error_type = type(exception).__name__
        self._error_message = str(exception)

        if exception.__traceback__ is not None:
            self._error_stack_trace = "".join(format_exception(exception))

        if self._extra is None:
            self._extra = {}

        self._extra.update(self._extract_exception_cause(exception))

    def _extract_exception_cause(
        self, exception: BaseException
    ) -> dict[str, str]:
        causes = {}
        cause = exception.__cause__ or exception.__context__
        cause_depth = 0

        while cause is not None:
            cause_depth += 1
            causes[self._depth_to_cause(cause_depth)] = cause.__class__.__name__
            cause = cause.__cause__ or cause.__context__

        return causes

    def _depth_to_cause(self, depth: int) -> str:
        match depth:
            case 1:
                return "causeOne"
            case 2:
                return "causeTwo"
            case 3:
                return "causeThree"
            case 4:
                return "causeFour"
            case 5:
                return "causeFive"
            case 6:
                return "causeSix"
            case 7:
                return "causeSeven"
            case 8:
                return "causeEight"
            case 9:
                return "causeNine"
            case _:
                return "causeN"

    def __str__(self) -> str:
        return f"level `{self._log_level.name}`, message `{self._message}`"

    def __repr__(self) -> str:
        return (
            "%s (\n\tlevel : `%s`,\n\tmessage : `%s`,\n\ttags : %s,\n\tlabel : %s,\n\terror_type : `%s`,\n\terror_message: `%s`\n)%s"
            % (
                self.__class__.__name__,
                self._log_level.name,
                self._message,
                self._tags or [],
                self._extra or {},
                self._error_type or "None",
                self._error_message or "None",
                f"\n{self._error_stack_trace}"
                if self._error_stack_trace is not None
                else "",
            )
        )


@dataclass
class SenderResponse:
    sent: bool
    reason: str | None = None
    should_retry: bool | None = None


class EndOfLogMarker:
    pass


class BaseRemoteLogSender(AsyncEventLoopMixin):
    _REMOTE_LOGS = Counter(
        name="successful_remote_logs",
        documentation="Successfully sent remote log count",
        labelnames=["log_level"],
    )
    _FAILED_REMOTE_LOGS = Counter(
        name="failed_remote_logs",
        documentation="Failed remote log count",
        labelnames=["log_level", "exception"],
    )
    _REMOTE_SENDER_STATE = PrometheusEnum(
        name="remote_sender_state",
        documentation="Remote sender state",
        states=["running", "stopped"],
    )

    def __init__(
        self,
        service_name: str,
        max_log_retry: int = 5,
        log_queue_size: int = 1000,
        failed_log_queue_size: int = 1000,
    ) -> None:
        self._sender = (
            f"qena_shared_lib.remotelogging.{self.__class__.__name__}"
        )
        self._service_name = service_name
        self._max_log_retry = max_log_retry
        self._started = False
        self._closed = False
        self._log_queue: Queue[RemoteLogRecord | EndOfLogMarker] = Queue(
            log_queue_size
        )
        self._dead_letter_log_queue: Queue[RemoteLogRecord | EndOfLogMarker] = (
            Queue(failed_log_queue_size)
        )
        self._level = LogLevel.INFO
        self._logger = LoggerFactory.get_logger(
            f"remotelogging.{self.__class__.__name__.lower()}"
        )

    async def start(self) -> None:
        if self._started:
            raise RuntimeError("remote sender already started")

        self._started = True
        self._closed = False
        self._close_future = self.loop.create_future()
        _, _ = await gather(
            self.loop.run_in_executor(executor=None, func=self._hook_on_start),
            self._hook_on_start_async(),
        )

        self.loop.create_task(self._flush_logs()).add_done_callback(
            self._on_log_flusher_closed
        )
        self._logger.info(
            "remote logger `%s` started accepting logs",
            self.__class__.__name__,
        )
        self._REMOTE_SENDER_STATE.state("running")

    def _hook_on_start(self) -> None:
        pass

    async def _hook_on_start_async(self) -> None:
        pass

    def _on_log_flusher_closed(self, task: Task[None]) -> None:
        if task.cancelled():
            self._close_future.set_result(None)

            return

        exception = task.exception()

        if exception is not None:
            self._close_future.set_exception(exception)

            return

        gather(
            self.loop.run_in_executor(executor=None, func=self._hook_on_stop),
            self._hook_on_stop_async(),
        ).add_done_callback(self._on_close_hook_done)

    def _on_close_hook_done(self, future: Future[tuple[None, None]]) -> None:
        if future.cancelled():
            self._close_future.set_result(None)

            return

        exception = future.exception()

        if exception is not None:
            self._close_future.set_exception(exception)

            return

        self._close_future.set_result(None)
        self._logger.debug(
            "remote http logger closed, will no longer accept logs"
        )

    def stop(self) -> Future[None]:
        if self._closed:
            raise RuntimeError("remote sender already closed")

        self._closed = True
        self._started = False

        try:
            self._log_queue.put_nowait(EndOfLogMarker())
            self._dead_letter_log_queue.put_nowait(EndOfLogMarker())
        except QueueFull:
            pass

        self._close_future.add_done_callback(self._on_close_future_done)

        return self._close_future

    def _on_close_future_done(self, future: Future[None]) -> None:
        del future

        self._REMOTE_SENDER_STATE.state("stopped")

    def _hook_on_stop(self) -> None:
        pass

    async def _hook_on_stop_async(self) -> None:
        pass

    async def _flush_logs(self) -> None:
        while (
            not self._closed
            or not self._log_queue.empty()
            or not self._dead_letter_log_queue.empty()
        ):
            log = None

            if not self._dead_letter_log_queue.empty():
                log = await self._dead_letter_log_queue.get()

                if isinstance(log, RemoteLogRecord):
                    if log.log_retries >= self._max_log_retry:
                        self._logger.exception(
                            "failed to send log too many times, falling back to stdout or stderr. \n%r",
                            log,
                        )

                        continue

                    log.log_retries += 1

            if log is None:
                log = await self._log_queue.get()

            if isinstance(log, EndOfLogMarker):
                if (
                    not self._log_queue.empty()
                    or not self._dead_letter_log_queue.empty()
                ):
                    continue

                break

            try:
                sender_response = await self._send(log)
            except Exception as e:
                self._put_to_dead_letter_log_queue(log)
                self._logger.exception(
                    "error occurred while sending log to remote logging facility"
                )
                self._FAILED_REMOTE_LOGS.labels(
                    log_level=log.log_level.name, exception=e.__class__.__name__
                ).inc()

                continue

            if not sender_response.sent:
                if (
                    sender_response.should_retry is None
                    or sender_response.should_retry
                ):
                    self._put_to_dead_letter_log_queue(log)
                else:
                    self._logger.error(
                        "failed log wasn't requeued, falling back to stdout or stderr.\n%r",
                        log,
                    )

                self._logger.warning(
                    "log wasn't sent successfully, reason : %s",
                    sender_response.reason or "No reason",
                )
            else:
                self._REMOTE_LOGS.labels(log_level=log.log_level.name).inc()
                self._logger.debug(
                    "log sent to remote logging facility.\n%r", log
                )

    async def _send(self, log: RemoteLogRecord) -> SenderResponse:
        del log

        raise NotImplementedError()

    def _put_to_dead_letter_log_queue(self, log: RemoteLogRecord) -> None:
        if self._closed:
            self._logger.error(
                "%s logger closed, falling back to stdout or stderr.\n%r",
                self._sender,
                log,
            )

            return

        try:
            self._dead_letter_log_queue.put_nowait(log)
        except QueueFull:
            self._logger.error(
                "unable to queue log, falling back to stdout or stderr.\n%r",
                log,
            )

    def log(
        self,
        level: LogLevel,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> None:
        self._enqueue_log(
            level=level,
            message=message,
            tags=tags,
            extra=extra,
            exception=exception,
        )

    def debug(
        self,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> None:
        self._enqueue_log(
            level=LogLevel.DEBUG,
            message=message,
            tags=tags,
            extra=extra,
            exception=exception,
        )

    def info(
        self,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> None:
        self._enqueue_log(
            level=LogLevel.INFO,
            message=message,
            tags=tags,
            extra=extra,
            exception=exception,
        )

    def warning(
        self,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> None:
        self._enqueue_log(
            level=LogLevel.WARNING,
            message=message,
            tags=tags,
            extra=extra,
            exception=exception,
        )

    def error(
        self,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> None:
        self._enqueue_log(
            level=LogLevel.ERROR,
            message=message,
            tags=tags,
            extra=extra,
            exception=exception,
        )

    def exception(
        self,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> None:
        if exception is None:
            _, exception, _ = exc_info()

        self.error(
            message=message,
            tags=tags,
            extra=extra,
            exception=exception,
        )

    def set_level(self, level: LogLevel) -> None:
        self._level = level

    def _enqueue_log(
        self,
        level: LogLevel,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> None:
        if self._closed:
            self._logger.warning("Remote logger is already close")

            return

        if level.value < self._level.value:
            return

        log = self._construct_log(
            level=level,
            message=message,
            tags=tags,
            extra=extra,
            exception=exception,
        )

        try:
            self._log_queue.put_nowait(log)
        except QueueFull:
            self._put_to_dead_letter_log_queue(log)

    def _construct_log(
        self,
        level: LogLevel,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        exception: BaseException | None = None,
    ) -> RemoteLogRecord:
        log = RemoteLogRecord(
            message=message,
            service_name=self._service_name,
            log_level=level,
            log_logger=self._sender,
        )

        if tags is not None:
            log.tags = tags

        if extra is not None and all(
            isinstance(k, str) and isinstance(v, str)
            for (k, v) in extra.items()
        ):
            log.extra = extra

        if exception:
            log.error_from_exception(exception)

        return log
