from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_snake

__all__ = [
    "CamelCaseAliasedBaseModel",
    "SnakeCaseAliasedBaseModel",
]


class CamelCaseAliasedBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
        strict=False,
    )


class SnakeCaseAliasedBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_snake,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
        strict=False,
    )
