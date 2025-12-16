from dataclasses import dataclass
from inspect import Parameter
from typing import Annotated, get_args, get_origin

__all__ = [
    "DependsOn",
    "validate_annotation",
]


@dataclass
class DependsOn:
    dependency: type


def validate_annotation(parameter: Parameter | type) -> type | None:
    if isinstance(parameter, Parameter):
        annotation = parameter.annotation
    else:
        annotation = parameter

    if annotation is Parameter.empty or get_origin(annotation) is not Annotated:
        return None

    args = get_args(annotation)

    if len(args) != 2:
        return None

    _, dependency_metadata = args

    if not isinstance(dependency_metadata, DependsOn):
        return None

    return dependency_metadata.dependency
