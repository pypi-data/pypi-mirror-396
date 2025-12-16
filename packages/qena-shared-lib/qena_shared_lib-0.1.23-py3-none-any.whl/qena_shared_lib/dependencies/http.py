from typing import Any, TypeVar

from fastapi import Depends, FastAPI, Request
from punq import Container, Scope, empty

__all__ = [
    "add_service",
    "DependsOn",
    "get_service",
]

D = TypeVar("D")


def get_container(app: FastAPI) -> Container:
    if not hasattr(app.state, "container"):
        raise RuntimeError(
            "application does include container, possibly not created with builder"
        )

    if not isinstance(app.state.container, Container):
        raise TypeError("container is not type of `punq.Container`")

    return app.state.container


def add_service(
    app: FastAPI,
    service: type[D],
    factory: object = empty,
    instance: D = empty,
    scope: Scope = Scope.transient,
    **kwargs: Any,
) -> None:
    get_container(app).register(
        service=service,
        factory=factory,
        instance=instance,
        scope=scope,
        **kwargs,
    )


def get_service(app: FastAPI, service_key: type[D]) -> D:
    service = get_container(app).resolve(service_key=service_key)

    if not isinstance(service, service_key):
        raise TypeError(f"`{service}` not a `{service_key}`")

    return service


class DependencyResolver:
    def __init__(self, dependency: type):
        self._dependency = dependency

    def __call__(self, request: Request) -> Any:
        return get_service(app=request.app, service_key=self._dependency)


def DependsOn(dependency: type) -> Any:
    return Depends(DependencyResolver(dependency))
