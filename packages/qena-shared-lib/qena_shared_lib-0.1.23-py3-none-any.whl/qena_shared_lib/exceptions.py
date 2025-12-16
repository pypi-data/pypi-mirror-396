from enum import Enum
from typing import Any

from fastapi import status
from typing_extensions import Self

from .enums import ServiceType

__all__ = [
    "BadGateway",
    "BadRequest",
    "ClientError",
    "Conflict",
    "ExpectationFailed",
    "FailedDependency",
    "Forbidden",
    "GatewayTimeout",
    "Gone",
    "HTTPServiceError",
    "HTTPVersionNotSupported",
    "IAmATeapot",
    "InsufficientStorage",
    "InternalServerError",
    "KafkaDisconnectedError",
    "LengthRequired",
    "Locked",
    "LoopDetected",
    "MethodNotAllowed",
    "MisdirectedRequest",
    "NetworkAuthenticationRequired",
    "NotAcceptable",
    "NotExtended",
    "NotFound",
    "NotImplemented",
    "PayloadTooLarge",
    "PaymentRequired",
    "PreconditionFailed",
    "PreconditionRequired",
    "ProxyAuthenticationRequired",
    "RabbitMQBlockedError",
    "RabbitMQConnectionUnhealthyError",
    "RabbitMQRpcRequestPendingError",
    "RabbitMQRpcRequestTimeoutError",
    "RabbitMQServiceException",
    "RangeNotSatisfiable",
    "RequestHeaderFieldsTooLarge",
    "RequestTimeout",
    "ServerError",
    "ServiceException",
    "ServiceUnavailable",
    "Severity",
    "TooEarly",
    "TooManyRequests",
    "Unauthorized",
    "UnavailableForLegalReasons",
    "UnprocessableEntity",
    "UnsupportedMediaType",
    "UpgradeRequired",
    "URITooLong",
    "VariantAlsoNegotiates",
]


class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class ServiceException(Exception):
    GENERAL_SEVERITY: Severity | None = None
    GENERAL_EXTRACT_EXC_INFO: bool | None = None

    def __init__(
        self,
        message: str,
        severity: Severity | None = None,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        remote_logging: bool | None = None,
        extract_exc_info: bool | None = None,
    ):
        self._message = message

        if severity is not None:
            self._severity = severity
        elif self.GENERAL_SEVERITY is not None:
            self._severity = self.GENERAL_SEVERITY
        else:
            self._severity = Severity.LOW

        self._tags = tags
        self._extra = extra

        if remote_logging is not None:
            self._remote_logging = remote_logging
        else:
            self._remote_logging = True

        if extract_exc_info is not None:
            self._extract_exc_info = extract_exc_info
        elif self.GENERAL_EXTRACT_EXC_INFO is not None:
            self._extract_exc_info = self.GENERAL_EXTRACT_EXC_INFO
        else:
            self._extract_exc_info = False

    @property
    def message(self) -> str:
        return self._message

    @property
    def severity(self) -> Severity | None:
        return self._severity

    @property
    def tags(self) -> list[str] | None:
        return self._tags

    @property
    def extra(self) -> dict[str, str] | None:
        return self._extra

    @property
    def remote_logging(self) -> bool | None:
        return self._remote_logging

    @property
    def extract_exc_info(self) -> bool | None:
        return self._extract_exc_info

    def __str__(self) -> str:
        return f"message `{self._message}`, tags {self._tags or []}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ( message: `{self._message}`, tags: {self._tags or []}, extra: {self._extra or {}} )"


class HTTPServiceError(ServiceException):
    GENERAL_STATUS_CODE: int | None = None

    def __init__(
        self,
        message: str,
        body: Any | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        response_code: int | None = None,
        corrective_action: str | None = None,
        severity: Severity | None = None,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        remote_logging: bool = True,
        extract_exc_info: bool = True,
    ):
        super().__init__(
            message=message,
            severity=severity,
            tags=tags,
            extra=extra,
            remote_logging=remote_logging,
            extract_exc_info=extract_exc_info,
        )

        self._body = body
        self._status_code: int | None = None

        if status_code is not None:
            self._status_code = status_code
        else:
            self._status_code = self.GENERAL_STATUS_CODE

        self._headers = headers
        self._response_code = response_code
        self._corrective_action = corrective_action

    @property
    def body(self) -> Any | None:
        return self._body

    @property
    def status_code(self) -> int | None:
        return self._status_code

    @property
    def headers(self) -> dict[str, str] | None:
        return self._headers

    @property
    def response_code(self) -> int | None:
        return self._response_code

    @property
    def corrective_action(self) -> str | None:
        return self._corrective_action

    def __str__(self) -> str:
        return f"message `{self._message}`, status_code {self._status_code or 500}, response_code {self._response_code or 0}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ( message: `{self._message}`, status_code: {self._status_code or 500}, response_code: {self._response_code or 0} )"


class ClientError(HTTPServiceError):
    GENERAL_SEVERITY = Severity.MEDIUM
    GENERAL_EXTRACT_EXC_INFO = False


class BadRequest(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_400_BAD_REQUEST


class Unauthorized(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_401_UNAUTHORIZED


class PaymentRequired(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_402_PAYMENT_REQUIRED


class Forbidden(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_403_FORBIDDEN


class NotFound(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_404_NOT_FOUND


class MethodNotAllowed(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_405_METHOD_NOT_ALLOWED


class NotAcceptable(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_406_NOT_ACCEPTABLE


class ProxyAuthenticationRequired(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED


class RequestTimeout(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_408_REQUEST_TIMEOUT


class Conflict(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_409_CONFLICT


class Gone(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_410_GONE


class LengthRequired(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_411_LENGTH_REQUIRED


class PreconditionFailed(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_412_PRECONDITION_FAILED


class PayloadTooLarge(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class URITooLong(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_414_REQUEST_URI_TOO_LONG


class UnsupportedMediaType(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class RangeNotSatisfiable(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE


class ExpectationFailed(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_417_EXPECTATION_FAILED


class IAmATeapot(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_418_IM_A_TEAPOT


class MisdirectedRequest(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_421_MISDIRECTED_REQUEST


class UnprocessableEntity(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY


class Locked(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_423_LOCKED


class FailedDependency(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_424_FAILED_DEPENDENCY


class TooEarly(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_425_TOO_EARLY


class UpgradeRequired(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_426_UPGRADE_REQUIRED


class PreconditionRequired(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_428_PRECONDITION_REQUIRED


class TooManyRequests(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_429_TOO_MANY_REQUESTS


class RequestHeaderFieldsTooLarge(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE


class UnavailableForLegalReasons(ClientError):
    GENERAL_STATUS_CODE = status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS


class ServerError(HTTPServiceError):
    GENERAL_SEVERITY = Severity.HIGH
    GENERAL_EXTRACT_EXC_INFO = True


class InternalServerError(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR


class NotImplemented(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_501_NOT_IMPLEMENTED


class BadGateway(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_502_BAD_GATEWAY


class ServiceUnavailable(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_503_SERVICE_UNAVAILABLE


class GatewayTimeout(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_504_GATEWAY_TIMEOUT


class HTTPVersionNotSupported(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED


class VariantAlsoNegotiates(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_506_VARIANT_ALSO_NEGOTIATES


class InsufficientStorage(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_507_INSUFFICIENT_STORAGE


class LoopDetected(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_508_LOOP_DETECTED


class NotExtended(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_510_NOT_EXTENDED


class NetworkAuthenticationRequired(ServerError):
    GENERAL_STATUS_CODE = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED


class RabbitMQServiceException(ServiceException):
    GENERAL_SEVERITY = Severity.HIGH
    GENERAL_EXTRACT_EXC_INFO = True
    GENERAL_CODE: int | None = None

    def __init__(
        self,
        message: str,
        code: int | None = None,
        data: Any | None = None,
        severity: Severity | None = None,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        remote_logging: bool | None = None,
        extract_exc_info: bool | None = None,
    ):
        super().__init__(
            message=message,
            severity=severity,
            tags=tags,
            extra=extra,
            remote_logging=remote_logging,
            extract_exc_info=extract_exc_info,
        )

        if code is not None:
            self._code = code
        elif self.GENERAL_CODE is not None:
            self._code = self.GENERAL_CODE
        else:
            self._code = 0

        self._data = data

    @property
    def code(self) -> int:
        return self._code

    @property
    def data(self) -> Any | None:
        return self._data

    def __str__(self) -> str:
        return f"message `{self.message}`, code {self.code}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ( message: `{self._message}`, code: {self._code} )"


class RabbitMQBlockedError(Exception):
    pass


class RabbitMQRpcRequestTimeoutError(Exception):
    pass


class RabbitMQRpcRequestPendingError(Exception):
    pass


class RabbitMQConnectionUnhealthyError(Exception):
    pass


class KafkaDisconnectedError(Exception):
    pass


class GenericServiceExceptionFactory:
    def __init__(
        self,
        message: str,
        severity: Severity | None = None,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        remote_logging: bool = True,
        extract_exc_info: bool = True,
    ):
        self._message = message
        self._severity = severity
        self._tags = tags
        self._extra = extra
        self._remote_logging = remote_logging
        self._extract_exc_info = extract_exc_info

        self._http_service_error: type[HTTPServiceError] = InternalServerError
        self._rabbitmq_service_exception: type[RabbitMQServiceException] = (
            RabbitMQServiceException
        )

        self._body: Any | None = None
        self._status_code: int | None = None
        self._headers: dict[str, str] | None = None
        self._response_code: int | None = None
        self._corrective_action: str | None = None
        self._code: int | None = None
        self._data: Any | None = None

    def for_http_service_error(
        self, http_service_error: type[HTTPServiceError]
    ) -> Self:
        self._http_service_error = http_service_error

        return self

    def for_rabbitmq_service_exception(
        self, rabbitmq_service_exception: type[RabbitMQServiceException]
    ) -> Self:
        self._rabbitmq_service_exception = rabbitmq_service_exception

        return self

    def with_http_service_error(
        self,
        body: Any | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        response_code: int | None = None,
        corrective_action: str | None = None,
    ) -> Self:
        self._body = body
        self._status_code = status_code
        self._headers = headers
        self._response_code = response_code
        self._corrective_action = corrective_action

        return self

    def with_rabbitmq_service_exception(
        self,
        code: int | None = None,
        data: Any | None = None,
    ) -> Self:
        self._code = code
        self._data = data

        return self

    def create(self, service_type: ServiceType) -> ServiceException:
        assert self._http_service_error is not None
        assert self._rabbitmq_service_exception is not None

        match service_type:
            case ServiceType.HTTP:
                return self._http_service_error(
                    message=self._message,
                    body=self._body,
                    status_code=self._status_code,
                    headers=self._headers,
                    response_code=self._response_code,
                    corrective_action=self._corrective_action,
                    severity=self._severity,
                    tags=self._tags,
                    extra=self._extra,
                    remote_logging=self._remote_logging,
                    extract_exc_info=self._extract_exc_info,
                )
            case ServiceType.RABBIT_MQ:
                return self._rabbitmq_service_exception(
                    message=self._message,
                    code=self._code,
                    data=self._data,
                    severity=self._severity,
                    tags=self._tags,
                    extra=self._extra,
                    remote_logging=self._remote_logging,
                    extract_exc_info=self._extract_exc_info,
                )
