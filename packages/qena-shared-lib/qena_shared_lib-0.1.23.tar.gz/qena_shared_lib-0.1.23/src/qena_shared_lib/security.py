from asyncio import Future
from enum import Enum
from os import environ
from typing import AbstractSet, Annotated, Any, cast

try:
    from jwt import JWT, AbstractJWKBase, jwk_from_dict
    from jwt.exceptions import JWTDecodeError
    from jwt.utils import get_int_from_datetime, get_time_from_int
    from passlib.context import CryptContext
except ImportError:
    pass
from fastapi import Depends, Header
from pydantic import BaseModel, Field, ValidationError

from .dependencies.http import DependsOn
from .exceptions import Unauthorized
from .utils import AsyncEventLoopMixin

__all__ = [
    "Authorization",
    "get_int_from_datetime",
    "get_time_from_int",
    "jwk_from_dict",
    "JwtAdapter",
    "PasswordHasher",
    "PermissionMatch",
    "UserInfo",
]


MESSAGE = "you are not authorized to access requested resource"
RESPONSE_CODE = int(
    environ.get("QENA_SHARED_LIB_SECURITY_UNAUTHORIZED_RESPONSE_CODE") or 0
)


class PasswordHasher(AsyncEventLoopMixin):
    def __init__(self, schemes: Any | None = None) -> None:
        self._crypt_context = CryptContext(
            schemes=schemes or ["bcrypt"], deprecated="auto"
        )

    def hash(self, password: str) -> Future[str]:
        return self.loop.run_in_executor(
            None, self._crypt_context.hash, password
        )

    def verify(self, password: str, password_hash: str) -> Future[bool]:
        return self.loop.run_in_executor(
            None, self._crypt_context.verify, password, password_hash
        )


class JwtAdapter(AsyncEventLoopMixin):
    def __init__(self) -> None:
        self._jwt = JWT()

    def encode(
        self,
        payload: dict[str, Any],
        key: AbstractJWKBase | None = None,
        algorithm: str = "HS256",
        optional_headers: dict[str, str] | None = None,
    ) -> Future[str]:
        return self.loop.run_in_executor(
            None, self._jwt.encode, payload, key, algorithm, optional_headers
        )

    def decode(
        self,
        message: str,
        key: AbstractJWKBase | None = None,
        do_verify: bool = True,
        algorithms: AbstractSet[str] | None = None,
        do_time_check: bool = True,
    ) -> Future[dict[str, Any]]:
        return self.loop.run_in_executor(
            None,
            self._jwt.decode,
            message,
            key,
            do_verify,
            algorithms,
            do_time_check,
        )


class UserInfo(BaseModel):
    user_id: str = Field(alias="userId")
    user_type: str = Field(alias="type")
    user_permissions: list[str] | None = Field(
        default=None, alias="permissions"
    )


async def extract_user_info(
    jwt_adapter: Annotated[JwtAdapter, DependsOn(JwtAdapter)],
    token: Annotated[
        str | None,
        Header(
            alias=environ.get("QENA_SHARED_LIB_SECURITY_TOKEN_HEADER")
            or "authorization"
        ),
    ] = None,
    user_agent: Annotated[
        str | None, Header(alias="user-agent", include_in_schema=False)
    ] = None,
) -> UserInfo:
    extra = {"userAgent": user_agent} if user_agent is not None else None

    if token is None:
        raise Unauthorized(
            message=MESSAGE,
            response_code=RESPONSE_CODE,
            extra=extra,
        )

    try:
        payload = await jwt_adapter.decode(
            message=token, do_verify=False, do_time_check=True
        )
    except JWTDecodeError as e:
        raise Unauthorized(
            message=MESSAGE,
            response_code=RESPONSE_CODE,
            extra=extra,
            extract_exc_info=True,
        ) from e

    try:
        user_info = UserInfo.model_validate(payload)
    except ValidationError as e:
        raise Unauthorized(
            message=MESSAGE,
            response_code=RESPONSE_CODE,
            extra=extra,
            extract_exc_info=True,
        ) from e

    return cast(UserInfo, user_info)


class PermissionMatch(Enum):
    SOME = 0
    ALL = 1


def Authorization(
    user_type: str | None = None,
    permissions: list[str] | None = None,
    permission_match_strategy: PermissionMatch | None = None,
) -> Any:
    return Depends(
        EndpointAclValidator(
            user_type=user_type,
            permissions=permissions,
            permission_match_strategy=permission_match_strategy,
        )
    )


class EndpointAclValidator:
    def __init__(
        self,
        user_type: str | None = None,
        permissions: list[str] | None = None,
        permission_match_strategy: PermissionMatch | None = None,
    ):
        self._user_type = user_type
        self._permissions = permissions
        self._permission_match_strategy = (
            permission_match_strategy or PermissionMatch.SOME
        )

        if self._permissions is not None:
            self._permissions = sorted(self._permissions)

    def __call__(
        self, user_info: Annotated[UserInfo, Depends(extract_user_info)]
    ) -> UserInfo:
        if self._user_type_match(user_info) and self._permissions_match(
            user_info
        ):
            return user_info

        raise Unauthorized(
            message=MESSAGE,
            response_code=RESPONSE_CODE,
            tags=[user_info.user_id],
            extra={
                "userId": user_info.user_id,
                "userType": user_info.user_type,
                "userPermissions": str(user_info.user_permissions or []),
                "requiredUserType": self._user_type or "None",
                "requiredPermissions": str(self._permissions or []),
                "permissionMatchStrategy": self._permission_match_strategy.name,
            },
        )

    def _user_type_match(self, user_info: UserInfo) -> bool:
        if self._user_type is None:
            return True

        if user_info.user_type is None:
            return False

        return user_info.user_type == self._user_type

    def _permissions_match(self, user_info: UserInfo) -> bool:
        if self._permissions is None:
            return True

        if user_info.user_permissions is None:
            return False

        if self._permission_match_strategy == PermissionMatch.ALL:
            return self._permissions == sorted(user_info.user_permissions)

        return any(
            permission in self._permissions
            for permission in user_info.user_permissions
        )
