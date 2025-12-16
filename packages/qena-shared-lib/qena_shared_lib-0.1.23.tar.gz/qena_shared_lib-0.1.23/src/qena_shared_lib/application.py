from enum import Enum
from typing import Any, TypeVar

from fastapi import APIRouter, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from punq import Container, Scope, empty
from starlette.types import Lifespan
from typing_extensions import Self

from .http import ControllerBase
from .http._exception_handlers import (
    AbstractHttpExceptionHandler,
    HttpGeneralExceptionHandler,
    HTTPServiceExceptionHandler,
    RequestValidationErrorHandler,
)

__all__ = [
    "Builder",
    "Environment",
    "FastAPI",
]


D = TypeVar("D")


class Environment(Enum):
    DEVELOPMENT = 0
    PRODUCTION = 1


class Builder:
    def __init__(self) -> None:
        self._environment = Environment.DEVELOPMENT
        self._debug = False
        self._title = "Qena shared lib"
        self._description = "Qena shared tools for microservice"
        self._version = "0.1.0"
        self._lifespan = None
        self._openapi_url: str | None = "/openapi.json"
        self._docs_url: str | None = "/docs"
        self._redoc_url: str | None = "/redoc"
        self._metrics_endpoint: str | None = None
        self._instrumentator: Instrumentator | None = None
        self._routers: list[APIRouter] = []
        self._container = Container()
        self._built = False

    def with_environment(self, environment: Environment) -> Self:
        match environment:
            case Environment.DEVELOPMENT:
                self._environment = Environment.DEVELOPMENT
                self._debug = True
            case Environment.PRODUCTION:
                self._environment = Environment.PRODUCTION
                self._debug = False
                self._openapi_url = None
                self._docs_url = None
                self._redoc_url = None

        return self

    def with_title(self, title: str) -> Self:
        self._title = title

        return self

    def with_description(self, description: str) -> Self:
        self._description = description

        return self

    def with_version(self, version: str) -> Self:
        self._version = version

        return self

    def with_lifespan(self, lifespan: Lifespan) -> Self:
        self._lifespan = lifespan

        return self

    def with_controllers(self, *controllers: type[ControllerBase]) -> Self:
        for index, controller in enumerate(controllers):
            if not isinstance(controller, type) or not issubclass(
                controller, ControllerBase
            ):
                raise TypeError(
                    f"controller {index} is {type(controller)}, expected instance of type or subclass of `ControllerBase`"
                )

            self._container.register(
                service=ControllerBase,
                factory=controller,
                scope=Scope.singleton,
            )

        return self

    def with_routers(self, *routers: APIRouter) -> Self:
        if any(not isinstance(router, APIRouter) for router in routers):
            raise TypeError("some routers are not type `APIRouter`")

        self._routers.extend(routers)

        return self

    def with_exception_handlers(
        self, *exception_handlers: type[AbstractHttpExceptionHandler]
    ) -> Self:
        for index, exception_handler in enumerate(exception_handlers):
            if not isinstance(exception_handler, type) or not issubclass(
                exception_handler, AbstractHttpExceptionHandler
            ):
                raise TypeError(
                    f"exception handler {index} is {type(exception_handler)}, expected instance of type or subclass of `AbstractHttpExceptionHandler`"
                )

            self._container.register(
                service=AbstractHttpExceptionHandler,
                factory=exception_handler,
                scope=Scope.singleton,
            )

        return self

    def with_default_exception_handlers(self) -> Self:
        self.with_exception_handlers(
            HttpGeneralExceptionHandler,
            HTTPServiceExceptionHandler,
            RequestValidationErrorHandler,
        )

        return self

    def with_singleton(
        self,
        service: type[D],
        factory: Any = empty,
        instance: Any = empty,
        **kwargs: Any,
    ) -> Self:
        self._container.register(
            service=service,
            factory=factory,
            instance=instance,
            scope=Scope.singleton,
            **kwargs,
        )

        return self

    def with_transient(
        self, service: type[D], factory: Any = empty, **kwargs: Any
    ) -> Self:
        self._container.register(
            service=service,
            factory=factory,
            scope=Scope.transient,
            **kwargs,
        )

        return self

    def with_metrics(self, endpoint: str = "/metrics") -> Self:
        self._metrics_endpoint = endpoint
        self._instrumentator = Instrumentator()

        return self

    def build(self) -> FastAPI:
        if self._built:
            raise RuntimeError("fastapi application aleady built")

        app = FastAPI(
            debug=self._debug,
            title=self._title,
            description=self._description,
            version=self._version,
            openapi_url=self._openapi_url,
            docs_url=self._docs_url,
            redoc_url=self._redoc_url,
            lifespan=self._lifespan,
        )
        app.state.container = self._container

        self._register_api_controllers(app)
        self._register_exception_handlers(app)

        if self._instrumentator is not None:
            self._instrumentator.instrument(app).expose(
                app=app,
                endpoint=self._metrics_endpoint or "/metrics",
                include_in_schema=False,
            )

        self._built = True

        return app

    def _register_api_controllers(self, app: FastAPI) -> None:
        for router in self._routers + self._resolve_api_controllers():
            app.include_router(router)

    def _resolve_api_controllers(self) -> list[APIRouter]:
        return [
            api_controller.register_route_handlers()
            for api_controller in self._container.resolve_all(ControllerBase)
        ]

    def _register_exception_handlers(self, app: FastAPI) -> None:
        for exception_handler in self._resolve_exception_handlers():
            if not callable(exception_handler):
                raise ValueError(
                    f"exception handler {exception_handler.__class__.__name__} is not callable"
                )

            app.exception_handler(exception_handler.exception)(
                exception_handler
            )

    def _resolve_exception_handlers(self) -> list[AbstractHttpExceptionHandler]:
        return [
            exception_handler
            for exception_handler in self._container.resolve_all(
                AbstractHttpExceptionHandler
            )
        ]

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def container(self) -> Container:
        return self._container
