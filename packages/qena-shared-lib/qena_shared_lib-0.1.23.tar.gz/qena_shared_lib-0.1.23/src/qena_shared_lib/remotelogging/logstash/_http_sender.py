from httpx import AsyncClient, Timeout

from ...logging import LoggerFactory
from .._base import RemoteLogRecord, SenderResponse
from ._base import BaseLogstashSender

__all__ = ["HTTPSender"]


class HTTPSender(BaseLogstashSender):
    def __init__(
        self,
        url: str,
        service_name: str,
        user: str | None = None,
        password: str | None = None,
        http_client_timeout: Timeout | float | None = None,
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

        self._url = url

        auth = None

        if user is not None and password is not None:
            auth = (
                user or "",
                password or "",
            )

        self._client = AsyncClient(
            auth=auth, timeout=http_client_timeout or 5.0
        )
        self._logger = LoggerFactory.get_logger("logstash.httpsender")

    async def _send(self, log: RemoteLogRecord) -> SenderResponse:
        send_log_response = await self._client.post(
            url=self._url,
            json=self.remote_log_record_to_ecs(log),
        )

        if not send_log_response.is_success:
            return SenderResponse(
                sent=False,
                reason=f"status_code : {send_log_response.status_code}, body : {send_log_response.text}",
                should_retry=send_log_response.is_server_error,
            )

        return SenderResponse(sent=True)

    async def _hook_on_stop_async(self) -> None:
        await self._client.aclose()
