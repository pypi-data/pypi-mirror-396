from asyncio import StreamWriter, open_connection
from typing import Any

from pydantic_core import to_json

from ...logging import LoggerFactory
from .._base import RemoteLogRecord, SenderResponse
from ._base import BaseLogstashSender

__all__ = ["TCPSender"]


class TCPSender(BaseLogstashSender):
    def __init__(
        self,
        host: str,
        port: int,
        service_name: str,
        max_log_retry: int = 5,
        log_queue_size: int = 100,
        failed_log_queue_size: int = 500,
    ):
        super().__init__(
            service_name=service_name,
            max_log_retry=max_log_retry,
            log_queue_size=log_queue_size,
            failed_log_queue_size=failed_log_queue_size,
        )

        self._client = AsyncTcpClient(host=host, port=port)
        self._logger = LoggerFactory.get_logger("logstash.tcpsender")

    async def _send(self, log: RemoteLogRecord) -> SenderResponse:
        await self._client.write(self.remote_log_record_to_ecs(log))

        return SenderResponse(sent=True)

    async def _hook_on_start_async(self) -> None:
        await self._client.open()

    async def _hook_on_stop_async(self) -> None:
        await self._client.close()


class AsyncTcpClient:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._writer: StreamWriter | None = None
        self._client_closed = False

    async def write(self, json: dict[str, Any]) -> None:
        if self._client_closed:
            raise RuntimeError("async tcp client already closed")

        if self._writer_closed():
            await self._connect()

        assert self._writer is not None

        self._writer.write(to_json(json))
        self._writer.write(b"\n")

        try:
            await self._writer.drain()
        except ConnectionResetError:
            await self._connect()

    async def open(self) -> None:
        await self._connect()

    async def close(self) -> None:
        if not self._writer_closed() and self._writer is not None:
            self._writer.write_eof()
            await self._writer.drain()
            self._writer.close()

            self._client_closed = True

    def _writer_closed(self) -> bool:
        return self._writer is None or self._writer.is_closing()

    async def _connect(self) -> None:
        _, self._writer = await open_connection(
            host=self._host, port=self._port
        )
