from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Sequence, TypeVar

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Cookie,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Security,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from fastapi.datastructures import Default
from fastapi.params import Depends
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.types import IncEx

__all__ = [
    "api_controller",
    "APIRouter",
    "BackgroundTasks",
    "Body",
    "ControllerBase",
    "Cookie",
    "delete",
    "Depends",
    "File",
    "FileResponse",
    "Form",
    "get",
    "head",
    "Header",
    "HTMLResponse",
    "HTTPException",
    "JSONResponse",
    "options",
    "patch",
    "Path",
    "PlainTextResponse",
    "post",
    "put",
    "Query",
    "RedirectResponse",
    "Request",
    "Response",
    "Response",
    "Security",
    "status",
    "StreamingResponse",
    "trace",
    "UploadFile",
    "WebSocket",
    "WebSocketDisconnect",
    "WebSocketException",
]

AC = TypeVar("AC")
API_CONTROLLER_ATTRIBUTE = "__api_controller_router__"
ROUTE_HANDLER_ATTRIBUTE = "__route_handler_metadata__"


class HTTPMethods(Enum):
    GET = 0
    PUT = 1
    POST = 2
    DELETE = 3
    OPTIONS = 4
    HEAD = 5
    PATCH = 6
    TRACE = 7


@dataclass
class RouteHandlerMetadata:
    method: HTTPMethods
    path: str | None = None
    response_model: Any | None = None
    status_code: int | None = None
    tags: list[str | Enum] | None = None
    dependencies: Sequence[Depends] | None = None
    summary: str | None = None
    description: str | None = None
    response_description: str = "Successful Response"
    responses: dict[int | str, dict[str, Any]] | None = None
    deprecated: bool | None = None
    response_model_include: IncEx | None = None
    response_model_exclude: IncEx | None = None
    response_model_by_alias: bool = True
    response_model_exclude_unset: bool = False
    response_model_exclude_defaults: bool = False
    response_model_exclude_none: bool = False
    include_in_schema: bool = True
    response_class: type[Response] = JSONResponse
    name: str | None = None
    openapi_extra: dict[str, Any] | None = None


def api_controller(
    prefix: str | None = None,
    *,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    default_response_class: type[Response] = JSONResponse,
    responses: dict[int | str, dict[str, Any]] | None = None,
    redirect_slashes: bool = True,
    deprecated: bool | None = None,
    include_in_schema: bool = True,
) -> Callable[[type["ControllerBase"]], type["ControllerBase"]]:
    def annotate_class(
        api_controller_class: type[ControllerBase],
    ) -> type[ControllerBase]:
        router = APIRouter(
            prefix=prefix or "",
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            redirect_slashes=redirect_slashes,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
        )

        setattr(api_controller_class, API_CONTROLLER_ATTRIBUTE, router)

        return api_controller_class

    return annotate_class


def get(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.GET,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


def put(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.PUT,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


def post(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.POST,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


def delete(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.DELETE,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


def options(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.OPTIONS,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


def head(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.HEAD,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


def patch(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.PATCH,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


def trace(
    path: str | None = None,
    *,
    response_model: Any | None = Default(None),
    status_code: int | None = None,
    tags: list[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(route_handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            route_handler,
            ROUTE_HANDLER_ATTRIBUTE,
            RouteHandlerMetadata(
                method=HTTPMethods.TRACE,
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                openapi_extra=openapi_extra,
            ),
        )

        return route_handler

    return wrapper


class ControllerBase:
    def get_api_router(self) -> APIRouter:
        api_router = getattr(self, API_CONTROLLER_ATTRIBUTE, None)

        if api_router is None:
            raise AttributeError(
                f"{self.__class__.__name__} not a api controller, possibly no annotated with either `ApiController`"
            )

        return api_router

    def register_route_handlers(self) -> APIRouter:
        api_router = self.get_api_router()

        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name, None)

            if attribute is None:
                continue

            route_handler_metadata = getattr(
                attribute, ROUTE_HANDLER_ATTRIBUTE, None
            )

            if route_handler_metadata is None:
                continue

            if not isinstance(route_handler_metadata, RouteHandlerMetadata):
                raise TypeError(
                    f"expected `{ROUTE_HANDLER_ATTRIBUTE}` to be of type `RouteHandlerMetadata`, got {type(route_handler_metadata)}"
                )

            api_router_method = None

            match route_handler_metadata.method:
                case HTTPMethods.GET:
                    api_router_method = api_router.get
                case HTTPMethods.PUT:
                    api_router_method = api_router.put
                case HTTPMethods.POST:
                    api_router_method = api_router.post
                case HTTPMethods.DELETE:
                    api_router_method = api_router.delete
                case HTTPMethods.OPTIONS:
                    api_router_method = api_router.options
                case HTTPMethods.HEAD:
                    api_router_method = api_router.head
                case HTTPMethods.PATCH:
                    api_router_method = api_router.patch
                case HTTPMethods.TRACE:
                    api_router_method = api_router.trace

            if api_router_method is None:
                raise ValueError(
                    f"api router method {route_handler_metadata.method} not supported"
                )

            api_router_method(
                path=route_handler_metadata.path or "",
                response_model=route_handler_metadata.response_model,
                status_code=route_handler_metadata.status_code,
                tags=route_handler_metadata.tags,
                dependencies=route_handler_metadata.dependencies,
                summary=route_handler_metadata.summary,
                description=route_handler_metadata.description,
                response_description=route_handler_metadata.response_description,
                responses=route_handler_metadata.responses,
                deprecated=route_handler_metadata.deprecated,
                response_model_include=route_handler_metadata.response_model_include,
                response_model_exclude=route_handler_metadata.response_model_exclude,
                response_model_by_alias=route_handler_metadata.response_model_by_alias,
                response_model_exclude_unset=route_handler_metadata.response_model_exclude_unset,
                response_model_exclude_defaults=route_handler_metadata.response_model_exclude_defaults,
                response_model_exclude_none=route_handler_metadata.response_model_exclude_none,
                include_in_schema=route_handler_metadata.include_in_schema,
                response_class=route_handler_metadata.response_class,
                name=route_handler_metadata.name,
                openapi_extra=route_handler_metadata.openapi_extra,
            )(attribute)

        return api_router
